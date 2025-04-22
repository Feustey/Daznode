import os
import codecs
import grpc
from typing import Dict, List, Any, Callable, Optional, AsyncGenerator
import asyncio
import logging
from datetime import datetime, timedelta

from core.config import settings

# Importer les protobuf générés LND
try:
    from proto import lightning_pb2 as ln
    from proto import lightning_pb2_grpc as lnrpc
    from proto import router_pb2 as router
    from proto import router_pb2_grpc as routerrpc
except ImportError:
    logging.error("Protobuf LND non trouvés. Générez-les avec la commande : python -m grpc_tools.protoc...")

logger = logging.getLogger(__name__)

class LNDClient:
    """Client pour interagir avec un nœud LND via gRPC"""
    
    def __init__(self, cert_path: str = None, macaroon_path: str = None, grpc_host: str = None):
        """Initialise le client LND
        
        Args:
            cert_path: Chemin vers le certificat TLS de LND
            macaroon_path: Chemin vers le macaroon admin de LND
            grpc_host: Hôte gRPC de LND (ex: localhost:10009)
        """
        self.cert_path = cert_path or settings.LND_TLS_CERT_PATH
        self.macaroon_path = macaroon_path or settings.LND_MACAROON_PATH
        self.grpc_host = grpc_host or settings.LND_GRPC_HOST
        
        if not self.cert_path or not self.macaroon_path:
            logger.warning("Certificat TLS ou macaroon non configurés. Certaines fonctionnalités seront désactivées.")
        
        self._stub = None
        self._router_stub = None
        self._channel = None
    
    def _get_credentials(self) -> grpc.ChannelCredentials:
        """Récupère les credentials pour la connexion gRPC"""
        cert = open(self.cert_path, 'rb').read()
        ssl_creds = grpc.ssl_channel_credentials(cert)
        return ssl_creds
    
    def _get_auth_metadata(self) -> grpc.CallCredentials:
        """Récupère les métadonnées d'authentification"""
        with open(self.macaroon_path, 'rb') as f:
            macaroon_bytes = f.read()
        macaroon = codecs.encode(macaroon_bytes, 'hex')
        auth_credentials = grpc.metadata_call_credentials(
            lambda context, callback: callback([('macaroon', macaroon)], None)
        )
        return auth_credentials
    
    def _create_stub(self):
        """Crée le stub gRPC pour LND"""
        if not self.cert_path or not os.path.exists(self.cert_path):
            raise ValueError(f"Certificat TLS non trouvé: {self.cert_path}")
            
        if not self.macaroon_path or not os.path.exists(self.macaroon_path):
            raise ValueError(f"Macaroon non trouvé: {self.macaroon_path}")
        
        # Combiner les credentials SSL et les métadonnées d'authentification
        ssl_creds = self._get_credentials()
        auth_creds = self._get_auth_metadata()
        combined_creds = grpc.composite_channel_credentials(ssl_creds, auth_creds)
        
        # Créer le canal gRPC
        channel = grpc.secure_channel(self.grpc_host, combined_creds)
        self._channel = channel
        
        # Créer les stubs
        self._stub = lnrpc.LightningStub(channel)
        self._router_stub = routerrpc.RouterStub(channel)
        
        return self._stub
    
    @property
    def stub(self):
        """Récupère le stub gRPC, en le créant si nécessaire"""
        if self._stub is None:
            self._create_stub()
        return self._stub
    
    @property
    def router_stub(self):
        """Récupère le stub du router, en le créant si nécessaire"""
        if self._router_stub is None:
            self._create_stub()
        return self._router_stub
    
    def get_node_info(self) -> Dict:
        """Récupère les informations sur le nœud local"""
        try:
            response = self.stub.GetInfo(ln.GetInfoRequest())
            # Gérer le cas où best_header_timestamp est un mock
            best_header_timestamp = None
            if hasattr(response, 'best_header_timestamp'):
                try:
                    best_header_timestamp = datetime.fromtimestamp(int(response.best_header_timestamp)).isoformat()
                except (TypeError, ValueError):
                    pass

            # Gérer les chaînes de manière sécurisée
            chains = []
            if hasattr(response, 'chains'):
                for c in response.chains:
                    try:
                        if isinstance(c, str):
                            chains.append(c)
                        else:
                            chains.append(c.chain)
                    except AttributeError:
                        pass

            # Gérer les features de manière sécurisée
            features = {}
            if hasattr(response, 'features') and response.features:
                try:
                    for k, v in response.features.items():
                        try:
                            features[k] = {
                                "name": str(v.name) if hasattr(v, 'name') else '',
                                "is_required": bool(v.is_required) if hasattr(v, 'is_required') else False,
                                "is_known": bool(v.is_known) if hasattr(v, 'is_known') else False
                            }
                        except AttributeError:
                            pass
                except (TypeError, AttributeError):
                    pass

            return {
                "pubkey": response.identity_pubkey,
                "alias": response.alias,
                "color": response.color,
                "version": response.version,
                "num_active_channels": response.num_active_channels,
                "num_inactive_channels": response.num_inactive_channels,
                "num_pending_channels": response.num_pending_channels,
                "block_height": response.block_height,
                "synced_to_chain": response.synced_to_chain,
                "synced_to_graph": response.synced_to_graph,
                "uris": response.uris,
                "best_header_timestamp": best_header_timestamp,
                "chains": chains,
                "features": features
            }
        except grpc.RpcError as e:
            logger.error(f"Erreur gRPC lors de la récupération des informations du nœud: {e}")
            raise
    
    def list_channels(self, active_only: bool = False, inactive_only: bool = False) -> List[Dict]:
        """Liste tous les canaux du nœud
        
        Args:
            active_only: Ne récupérer que les canaux actifs
            inactive_only: Ne récupérer que les canaux inactifs
        """
        try:
            request = ln.ListChannelsRequest()
            if active_only:
                request.active_only = True
            elif inactive_only:
                request.inactive_only = True
            response = self.stub.ListChannels(request)
            
            channels = []
            for channel in response.channels:
                if active_only and not channel.active:
                    continue
                if inactive_only and channel.active:
                    continue
                # Gérer les HTLCs de manière sécurisée
                pending_htlcs = []
                if hasattr(channel, 'pending_htlcs'):
                    try:
                        for h in channel.pending_htlcs:
                            htlc = {
                                "incoming": h.incoming,
                                "amount": h.amount,
                                "expiration_height": h.expiration_height,
                                "htlc_index": h.htlc_index
                            }
                            if hasattr(h, 'hash_lock') and h.hash_lock:
                                try:
                                    htlc["hash_lock"] = h.hash_lock.hex()
                                except AttributeError:
                                    htlc["hash_lock"] = str(h.hash_lock)
                            pending_htlcs.append(htlc)
                    except (TypeError, AttributeError):
                        pass

                # Convertir les IDs en chaînes
                try:
                    channel_id = str(channel.channel_id if hasattr(channel, 'channel_id') else channel.chan_id)
                except (TypeError, AttributeError):
                    channel_id = ''

                channels.append({
                    "channel_id": channel_id,
                    "remote_pubkey": channel.remote_pubkey,
                    "capacity": channel.capacity,
                    "local_balance": channel.local_balance,
                    "remote_balance": channel.remote_balance,
                    "unsettled_balance": channel.unsettled_balance,
                    "active": channel.active,
                    "private": channel.private,
                    "initiator": channel.initiator,
                    "total_satoshis_sent": channel.total_satoshis_sent,
                    "total_satoshis_received": channel.total_satoshis_received,
                    "num_updates": channel.num_updates,
                    "commit_fee": channel.commit_fee,
                    "commit_weight": channel.commit_weight,
                    "fee_per_kw": channel.fee_per_kw,
                    "chan_status_flags": channel.chan_status_flags,
                    "local_chan_reserve_sat": channel.local_chan_reserve_sat,
                    "remote_chan_reserve_sat": channel.remote_chan_reserve_sat,
                    "local_balance_msat": channel.local_balance_msat,
                    "remote_balance_msat": channel.remote_balance_msat,
                    "pending_htlcs": pending_htlcs
                })
            
            return channels
        except grpc.RpcError as e:
            logger.error(f"Erreur gRPC lors de la récupération des canaux: {e}")
            raise
    
    def open_channel(self, node_pubkey: str, local_amount: int, push_amount: int = 0, 
                     private: bool = False, min_htlc_msat: int = 1000, 
                     remote_csv_delay: int = 144, spend_unconfirmed: bool = False) -> str:
        """Ouvre un nouveau canal avec un nœud distant
        
        Args:
            node_pubkey: Clé publique du nœud distant
            local_amount: Montant à allouer au canal en sats
            push_amount: Montant à pousser au nœud distant en sats
            private: Si True, le canal sera privé (non annoncé)
            min_htlc_msat: Montant minimum pour les HTLC en millisionièmes de satoshi
            remote_csv_delay: Délai CSV pour le nœud distant
            spend_unconfirmed: Si True, permet d'utiliser des fonds non confirmés
        
        Returns:
            Channel point (outpoint) sous forme txid:output_index
        """
        try:
            # Convertir la clé publique de hex à bytes
            pubkey_bytes = bytes.fromhex(node_pubkey)
            
            request = ln.OpenChannelRequest(
                node_pubkey=pubkey_bytes,
                local_funding_amount=local_amount,
                push_sat=push_amount,
                private=private,
                min_htlc_msat=min_htlc_msat,
                remote_csv_delay=remote_csv_delay,
                spend_unconfirmed=spend_unconfirmed
            )
            
            response = self.stub.OpenChannelSync(request)
            
            # Le channel point est sous la forme txid:output_index
            funding_txid_bytes = response.funding_txid_bytes[::-1].hex()
            channel_point = f"{funding_txid_bytes}:{response.output_index}"
            
            return channel_point
        except grpc.RpcError as e:
            logger.error(f"Erreur gRPC lors de l'ouverture du canal: {e}")
            raise
    
    def close_channel(self, channel_point: str, force: bool = False, target_conf: int = 6) -> str:
        """Ferme un canal existant
        
        Args:
            channel_point: Point de canal sous forme txid:output_index
            force: Si True, force la fermeture du canal
            target_conf: Nombre de confirmations visé pour la transaction de fermeture
        
        Returns:
            Transaction ID de la transaction de fermeture
        """
        try:
            # Parser le channel point
            txid, output_index = channel_point.split(':')
            
            # Construire le ChannelPoint
            cp = ln.ChannelPoint(
                funding_txid_str=txid,
                output_index=int(output_index)
            )
            
            request = ln.CloseChannelRequest(
                channel_point=cp,
                force=force,
                target_conf=target_conf
            )
            
            # CloseChannel est un stream RPC
            for update in self.stub.CloseChannel(request):
                if update.HasField('close_pending'):
                    logger.info(f"Fermeture du canal en attente. Txid: {update.close_pending.txid.hex()}")
                elif update.HasField('chan_close'):
                    close_type = ["COOPERATIVE", "LOCAL_FORCE", "REMOTE_FORCE", "BREACH", "FUNDING_CANCELED", "ABANDONED"][update.chan_close.close_type]
                    logger.info(f"Canal fermé. Type: {close_type}. Txid: {update.chan_close.closing_txid.hex()}")
                    return update.chan_close.closing_txid.hex()
            
            return None
        except grpc.RpcError as e:
            logger.error(f"Erreur gRPC lors de la fermeture du canal: {e}")
            raise
    
    def update_channel_policy(self, channel_point: str, base_fee_msat: int = None, 
                              fee_rate: int = None, time_lock_delta: int = None) -> bool:
        """Met à jour la politique de frais d'un canal
        
        Args:
            channel_point: Point de canal sous forme txid:output_index
            base_fee_msat: Frais de base en millisionièmes de satoshi
            fee_rate: Taux de frais proportionnel en parties par million
            time_lock_delta: Delta de verrouillage temporel
            
        Returns:
            True si la mise à jour a réussi
        """
        try:
            # Parser le channel point
            txid, output_index = channel_point.split(':')
            
            # Construire le ChannelPoint
            cp = ln.ChannelPoint(
                funding_txid_str=txid,
                output_index=int(output_index)
            )
            
            # Créer un masque pour les champs à mettre à jour
            update_mask = 0
            if base_fee_msat is not None:
                update_mask |= 1
            if fee_rate is not None:
                update_mask |= 2
            if time_lock_delta is not None:
                update_mask |= 4
            
            request = ln.PolicyUpdateRequest(
                chan_point=cp,
                base_fee_msat=base_fee_msat if base_fee_msat is not None else 0,
                fee_rate=fee_rate / 1000000 if fee_rate is not None else 0,  # Convertir ppm en valeur décimale
                time_lock_delta=time_lock_delta if time_lock_delta is not None else 0,
                max_htlc_msat=0,  # Non mis à jour
                min_htlc_msat=0,  # Non mis à jour
                min_htlc_msat_specified=False,
                max_htlc_msat_specified=False,
                fee_rate_ppm=fee_rate if fee_rate is not None else 0
            )
            
            self.stub.UpdateChannelPolicy(request)
            return True
        except grpc.RpcError as e:
            logger.error(f"Erreur gRPC lors de la mise à jour de la politique du canal: {e}")
            raise
    
    def get_forwarding_history(self, start_time: int = None, end_time: int = None, 
                               offset: int = 0, limit: int = 100) -> Dict:
        """Récupère l'historique de routage pour une période donnée
        
        Args:
            start_time: Timestamp UNIX de début
            end_time: Timestamp UNIX de fin
            offset: Offset pour la pagination
            limit: Nombre maximum d'entrées à récupérer
        
        Returns:
            Historique des transferts avec les détails
        """
        try:
            # Si les timestamps ne sont pas spécifiés, utiliser une période par défaut (1 semaine)
            now = int(datetime.now().timestamp())
            if end_time is None:
                end_time = now
            if start_time is None:
                start_time = now - 7 * 24 * 60 * 60  # 7 jours
            
            request = ln.ForwardingHistoryRequest(
                start_time=start_time,
                end_time=end_time,
                limit=limit
            )
            
            response = self.stub.ForwardingHistory(request)
            
            forwarding_events = []
            for event in response.forwarding_events:
                forwarding_events.append({
                    "timestamp": datetime.fromtimestamp(event.timestamp).isoformat(),
                    "chan_id_in": str(event.chan_id_in),
                    "chan_id_out": str(event.chan_id_out),
                    "amt_in": event.amt_in,
                    "amt_out": event.amt_out,
                    "fee": event.fee,
                    "fee_msat": event.fee_msat,
                    "amt_in_msat": event.amt_in_msat,
                    "amt_out_msat": event.amt_out_msat,
                })
            
            return {
                "forwarding_events": forwarding_events,
                "last_offset_index": response.last_offset_index,
                "total_count": len(forwarding_events)
            }
        except grpc.RpcError as e:
            logger.error(f"Erreur gRPC lors de la récupération de l'historique de transfert: {e}")
            raise
    
    async def subscribe_channel_events(self, callback: Callable) -> None:
        """Souscrit aux événements de canal (ouverture, fermeture, etc.)
        
        Args:
            callback: Fonction appelée pour chaque événement avec les arguments (event_type, data)
        """
        try:
            request = ln.ChannelEventSubscription()
            
            for update in self.stub.SubscribeChannelEvents(request):
                event_type = None
                data = {}
                
                if update.HasField('open_channel'):
                    event_type = "open_channel"
                    channel = update.open_channel
                    data = {
                        "channel_id": channel.chan_id,
                        "remote_pubkey": channel.remote_pubkey,
                        "capacity": channel.capacity,
                    }
                elif update.HasField('closed_channel'):
                    event_type = "closed_channel"
                    channel = update.closed_channel
                    data = {
                        "channel_id": channel.chan_id,
                        "remote_pubkey": channel.remote_pubkey,
                        "capacity": channel.capacity,
                        "close_type": channel.close_type,
                    }
                elif update.HasField('active_channel'):
                    event_type = "active_channel"
                    channel = update.active_channel
                    data = {
                        "channel_id": channel.chan_id,
                        "remote_pubkey": channel.remote_pubkey,
                    }
                elif update.HasField('inactive_channel'):
                    event_type = "inactive_channel"
                    channel = update.inactive_channel
                    data = {
                        "channel_id": channel.chan_id,
                        "remote_pubkey": channel.remote_pubkey,
                    }
                elif update.HasField('pending_open_channel'):
                    event_type = "pending_open_channel"
                    channel = update.pending_open_channel
                    data = {
                        "channel_id": channel.channel.chan_id,
                        "remote_pubkey": channel.channel.remote_pubkey,
                    }
                
                if event_type:
                    await callback(event_type, data)
        except grpc.RpcError as e:
            logger.error(f"Erreur gRPC lors de l'abonnement aux événements de canal: {e}")
            raise
    
    async def subscribe_invoice_events(self, callback: Callable) -> None:
        """Souscrit aux événements d'invoice
        
        Args:
            callback: Fonction appelée pour chaque événement avec l'argument (invoice)
        """
        try:
            request = ln.InvoiceSubscription(add_index=0, settle_index=0)
            
            for invoice in self.stub.SubscribeInvoices(request):
                await callback(self._format_invoice(invoice))
        except grpc.RpcError as e:
            logger.error(f"Erreur gRPC lors de l'abonnement aux événements d'invoice: {e}")
            raise
    
    def _format_invoice(self, invoice) -> Dict:
        """Formate une invoice LND en dictionnaire"""
        return {
            "memo": invoice.memo,
            "r_preimage": invoice.r_preimage.hex(),
            "r_hash": invoice.r_hash.hex(),
            "value": invoice.value,
            "value_msat": invoice.value_msat,
            "settled": invoice.settled,
            "creation_date": datetime.fromtimestamp(invoice.creation_date).isoformat(),
            "settle_date": datetime.fromtimestamp(invoice.settle_date).isoformat() if invoice.settle_date > 0 else None,
            "payment_request": invoice.payment_request,
            "description_hash": invoice.description_hash.hex(),
            "expiry": invoice.expiry,
            "fallback_addr": invoice.fallback_addr,
            "cltv_expiry": invoice.cltv_expiry,
            "route_hints": [
                {
                    "hop_hints": [
                        {
                            "node_id": hint.node_id.hex(),
                            "chan_id": hint.chan_id,
                            "fee_base_msat": hint.fee_base_msat,
                            "fee_proportional_millionths": hint.fee_proportional_millionths,
                            "cltv_expiry_delta": hint.cltv_expiry_delta
                        } for hint in router.hop_hints
                    ]
                } for route in invoice.route_hints
            ],
            "private": invoice.private,
            "add_index": invoice.add_index,
            "settle_index": invoice.settle_index,
            "amt_paid": invoice.amt_paid,
            "amt_paid_sat": invoice.amt_paid_sat,
            "amt_paid_msat": invoice.amt_paid_msat,
            "state": ln.Invoice.InvoiceState.Name(invoice.state),
            "htlcs": [
                {
                    "chan_id": htlc.chan_id,
                    "htlc_index": htlc.htlc_index,
                    "amt_msat": htlc.amt_msat,
                    "accept_height": htlc.accept_height,
                    "accept_time": htlc.accept_time,
                    "resolve_time": htlc.resolve_time,
                    "expiry_height": htlc.expiry_height,
                    "state": ln.InvoiceHTLCState.Name(htlc.state),
                    "custom_records": {k: v.hex() for k, v in htlc.custom_records.items()},
                    "mpp_total_amt_msat": htlc.mpp_total_amt_msat
                } for htlc in invoice.htlcs
            ],
            "features": {k: {"name": v.name, "is_required": v.is_required, "is_known": v.is_known} 
                        for k, v in invoice.features.items()},
            "is_keysend": invoice.is_keysend,
            "payment_addr": invoice.payment_addr.hex(),
            "is_amp": invoice.is_amp,
            "amp_invoice_state": {
                k: {
                    "state": ln.InvoiceHTLCState.Name(v.state),
                    "settle_index": v.settle_index,
                    "settle_time": v.settle_time,
                    "amt_paid_msat": v.amt_paid_msat
                } for k, v in invoice.amp_invoice_state.items()
            }
        }
    
    async def rebalance_channels(self, source_channels: List[str], target_channels: List[str], 
                                amount_sat: int, fee_limit_sat: int = 100) -> Dict:
        """Rééquilibre les fonds entre les canaux spécifiés
        
        Args:
            source_channels: Liste des IDs de canaux source
            target_channels: Liste des IDs de canaux cible
            amount_sat: Montant à rééquilibrer en satoshis
            fee_limit_sat: Limite de frais en satoshis
            
        Returns:
            Résultat du rééquilibrage
        """
        try:
            if not source_channels or not target_channels:
                raise ValueError("Les canaux source et cible sont requis")
                
            source_channels_int = [int(c) for c in source_channels]
            target_channels_int = [int(c) for c in target_channels]
            
            # Construire la requête SendToRouteRequest
            request = router.SendToRouteRequest(
                payment_hash=os.urandom(32),  # Hash aléatoire
                amt_msat=amount_sat * 1000,
                outgoing_chan_id=source_channels_int[0],  # Utiliser le premier canal source
                fee_limit_sat=fee_limit_sat
            )
            
            # Intégrer les restrictions de canal dans les hints
            outgoing_chan_ids = source_channels_int
            last_hop_channel_ids = target_channels_int
            
            # Exécuter le rééquilibrage
            response = self.router_stub.SendToRoute(request)
            
            if response.failure:
                return {
                    "success": False,
                    "error": {
                        "code": response.failure.code,
                        "channel_update": {
                            "signature": response.failure.channel_update.signature.hex(),
                            "chain_hash": response.failure.channel_update.chain_hash.hex(),
                            "chan_id": response.failure.channel_update.chan_id,
                            "timestamp": response.failure.channel_update.timestamp,
                            "message_flags": response.failure.channel_update.message_flags,
                            "channel_flags": response.failure.channel_update.channel_flags,
                            "time_lock_delta": response.failure.channel_update.time_lock_delta,
                            "htlc_minimum_msat": response.failure.channel_update.htlc_minimum_msat,
                            "base_fee": response.failure.channel_update.base_fee,
                            "fee_rate": response.failure.channel_update.fee_rate,
                            "htlc_maximum_msat": response.failure.channel_update.htlc_maximum_msat,
                            "extra_opaque_data": response.failure.channel_update.extra_opaque_data.hex()
                        },
                        "htlc_msat": response.failure.htlc_msat,
                        "onion_sha_256": response.failure.onion_sha_256.hex(),
                        "cltv_expiry": response.failure.cltv_expiry,
                        "flags": response.failure.flags,
                        "failure_source_index": response.failure.failure_source_index,
                        "height": response.failure.height
                    }
                }
            else:
                return {
                    "success": True,
                    "preimage": response.preimage.hex(),
                    "route": {
                        "total_time_lock": response.route.total_time_lock,
                        "total_fees": response.route.total_fees,
                        "total_amt": response.route.total_amt,
                        "hops": [
                            {
                                "chan_id": hop.chan_id,
                                "chan_capacity": hop.chan_capacity,
                                "amt_to_forward": hop.amt_to_forward,
                                "fee": hop.fee,
                                "expiry": hop.expiry,
                                "amt_to_forward_msat": hop.amt_to_forward_msat,
                                "fee_msat": hop.fee_msat,
                                "pub_key": hop.pub_key,
                                "tlv_payload": hop.tlv_payload,
                                "mpp_record": {
                                    "payment_addr": hop.mpp_record.payment_addr.hex() if hop.mpp_record else None,
                                    "total_amt_msat": hop.mpp_record.total_amt_msat if hop.mpp_record else None
                                } if hop.HasField('mpp_record') else None,
                                "amp_record": {
                                    "root_share": hop.amp_record.root_share.hex() if hop.amp_record else None,
                                    "set_id": hop.amp_record.set_id.hex() if hop.amp_record else None,
                                    "child_index": hop.amp_record.child_index if hop.amp_record else None
                                } if hop.HasField('amp_record') else None,
                                "custom_records": {k: v.hex() for k, v in hop.custom_records.items()}
                            } for hop in response.route.hops
                        ],
                        "total_fees_msat": response.route.total_fees_msat,
                        "total_amt_msat": response.route.total_amt_msat
                    }
                }
        except grpc.RpcError as e:
            logger.error(f"Erreur gRPC lors du rééquilibrage des canaux: {e}")
            raise 