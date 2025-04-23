import Link from 'next/link';
import { GithubIcon, TwitterIcon } from 'lucide-react';

const footerLinks = [
  {
    title: 'Documentation',
    items: [
      { name: 'Guide', href: '/docs/guide' },
      { name: 'API', href: '/docs/api' },
      { name: 'FAQ', href: '/docs/faq' },
    ],
  },
  {
    title: 'Communauté',
    items: [
      { name: 'Discord', href: 'https://discord.gg/daznode' },
      { name: 'Forum', href: 'https://forum.daznode.com' },
      { name: 'Blog', href: '/blog' },
    ],
  },
  {
    title: 'Légal',
    items: [
      { name: 'Confidentialité', href: '/privacy' },
      { name: 'Conditions', href: '/terms' },
      { name: 'Licence', href: '/license' },
    ],
  },
];

export default function Footer() {
  return (
    <footer className="bg-card mt-auto border-t border-border">
      <div className="max-w-7xl mx-auto py-12 px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
          {footerLinks.map((group) => (
            <div key={group.title}>
              <h3 className="text-sm font-semibold text-foreground tracking-wider uppercase">
                {group.title}
              </h3>
              <ul className="mt-4 space-y-4">
                {group.items.map((item) => (
                  <li key={item.name}>
                    <Link
                      href={item.href}
                      className="text-sm text-muted-foreground hover:text-foreground transition-colors"
                    >
                      {item.name}
                    </Link>
                  </li>
                ))}
              </ul>
            </div>
          ))}

          <div>
            <h3 className="text-sm font-semibold text-foreground tracking-wider uppercase">
              Suivez-nous
            </h3>
            <div className="mt-4 flex space-x-6">
              <a
                href="https://twitter.com/daznode"
                className="text-muted-foreground hover:text-foreground transition-colors"
                target="_blank"
                rel="noopener noreferrer"
              >
                <span className="sr-only">Twitter</span>
                <TwitterIcon className="h-6 w-6" />
              </a>
              <a
                href="https://github.com/daznode"
                className="text-muted-foreground hover:text-foreground transition-colors"
                target="_blank"
                rel="noopener noreferrer"
              >
                <span className="sr-only">GitHub</span>
                <GithubIcon className="h-6 w-6" />
              </a>
            </div>
          </div>
        </div>

        <div className="mt-8 border-t border-border pt-8 flex items-center justify-between">
          <p className="text-sm text-muted-foreground">
            &copy; {new Date().getFullYear()} Daznode. Tous droits réservés.
          </p>
          <img src="/logo.svg" alt="Logo Daznode" className="h-8 w-auto opacity-50" />
        </div>
      </div>
    </footer>
  );
} 