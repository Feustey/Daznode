import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { Cog6ToothIcon } from '@heroicons/react/24/outline';
import { cn } from '@/lib/utils';

interface NavItem {
  name: string;
  path: string;
}

const navItems: NavItem[] = [
  { name: 'General', path: '/' },
  { name: 'Channels', path: '/channels' },
  { name: 'Channel Map', path: '/channel-map' },
  { name: 'Closed Channels', path: '/closed-channels' },
  { name: 'Fee Report', path: '/fee-report' },
  { name: 'Performance', path: '/performance' },
  { name: 'Unprofitable Channels', path: '/unprofitable-channels' },
  { name: 'Socials', path: '/socials' },
];

export default function NavBar() {
  const pathname = usePathname();

  return (
    <nav className="bg-card-dark border-b border-gray-800">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              {/* Logo si nécessaire */}
            </div>
            <div className="hidden md:block">
              <div className="ml-10 flex items-baseline space-x-4">
                {navItems.map((item) => {
                  const isActive = pathname === item.path;
                  return (
                    <Link
                      key={item.name}
                      href={item.path}
                      className={cn(
                        'px-3 py-2 rounded-md text-sm font-medium transition-colors',
                        isActive
                          ? 'bg-gray-900 text-white'
                          : 'text-gray-300 hover:bg-gray-700 hover:text-white'
                      )}
                    >
                      {item.name}
                    </Link>
                  );
                })}
              </div>
            </div>
          </div>
          <div className="hidden md:block">
            <div className="ml-4 flex items-center md:ml-6">
              <Link href="/settings">
                <button
                  type="button"
                  className="rounded-full p-1 hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-gray-800 focus:ring-white"
                >
                  <Cog6ToothIcon className="h-6 w-6" aria-hidden="true" />
                </button>
              </Link>
            </div>
          </div>
          <div className="-mr-2 flex md:hidden">
            {/* Menu mobile à ajouter si nécessaire */}
          </div>
        </div>
      </div>

      {/* Menu mobile à ajouter si nécessaire */}
    </nav>
  );
} 