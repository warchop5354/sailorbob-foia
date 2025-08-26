'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import {
  MagnifyingGlassIcon,
  DocumentTextIcon,
  CloudArrowUpIcon,
  ChartBarIcon,
  UserIcon,
  Bars3Icon,
  XMarkIcon,
} from '@heroicons/react/24/outline';
import { User } from '@/types';
import { getAuthToken, removeAuthToken } from '@/lib/api';

interface NavItem {
  name: string;
  href: string;
  icon: React.ComponentType<any>;
  requiresAuth?: boolean;
  requiredRole?: User['role'];
}

const navigation: NavItem[] = [
  { name: 'Home', href: '/', icon: DocumentTextIcon },
  { name: 'Search', href: '/search', icon: MagnifyingGlassIcon },
  { name: 'Browse', href: '/documents', icon: DocumentTextIcon },
  { name: 'Upload', href: '/upload', icon: CloudArrowUpIcon, requiresAuth: true },
  { name: 'Admin', href: '/admin', icon: ChartBarIcon, requiresAuth: true, requiredRole: 'admin' },
];

export default function Navigation() {
  const [isOpen, setIsOpen] = useState(false);
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const pathname = usePathname();

  useEffect(() => {
    // Check if user is logged in
    const token = getAuthToken();
    if (token) {
      // In a real app, you'd validate the token and get user info
      // For now, we'll just assume they're logged in
      setUser({
        id: 1,
        username: 'demo_user',
        email: 'demo@example.com',
        first_name: 'Demo',
        last_name: 'User',
        role: 'user',
        created_at: new Date().toISOString(),
      });
    }
    setIsLoading(false);
  }, []);

  const handleLogout = () => {
    removeAuthToken();
    setUser(null);
    window.location.href = '/';
  };

  const filteredNavigation = navigation.filter((item) => {
    if (item.requiresAuth && !user) return false;
    if (item.requiredRole && user?.role !== item.requiredRole && user?.role !== 'admin') return false;
    return true;
  });

  return (
    <nav className="bg-gray-800 border-b border-gray-700">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          {/* Logo and main navigation */}
          <div className="flex">
            <div className="flex-shrink-0 flex items-center">
              <Link href="/" className="text-xl font-bold text-blue-400 hover:text-blue-300">
                SailorBob FOIA
              </Link>
            </div>
            <div className="hidden sm:ml-6 sm:flex sm:space-x-8">
              {filteredNavigation.map((item) => {
                const isActive = pathname === item.href;
                return (
                  <Link
                    key={item.name}
                    href={item.href}
                    className={`inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium transition-colors ${
                      isActive
                        ? 'border-blue-500 text-blue-400'
                        : 'border-transparent text-gray-300 hover:border-gray-300 hover:text-gray-200'
                    }`}
                  >
                    <item.icon className="w-4 h-4 mr-2" />
                    {item.name}
                  </Link>
                );
              })}
            </div>
          </div>

          {/* User menu */}
          <div className="hidden sm:ml-6 sm:flex sm:items-center">
            {!isLoading && (
              <>
                {user ? (
                  <div className="flex items-center space-x-4">
                    <span className="text-sm text-gray-300">
                      Welcome, {user.first_name || user.username}
                    </span>
                    <div className="relative">
                      <Link
                        href="/profile"
                        className="flex items-center text-sm text-gray-300 hover:text-gray-200"
                      >
                        <UserIcon className="w-5 h-5 mr-1" />
                        Profile
                      </Link>
                    </div>
                    <button
                      onClick={handleLogout}
                      className="text-sm text-gray-300 hover:text-gray-200"
                    >
                      Logout
                    </button>
                  </div>
                ) : (
                  <div className="flex items-center space-x-4">
                    <Link
                      href="/login"
                      className="text-sm text-gray-300 hover:text-gray-200"
                    >
                      Login
                    </Link>
                    <Link
                      href="/register"
                      className="btn-primary text-sm"
                    >
                      Register
                    </Link>
                  </div>
                )}
              </>
            )}
          </div>

          {/* Mobile menu button */}
          <div className="flex items-center sm:hidden">
            <button
              onClick={() => setIsOpen(!isOpen)}
              className="inline-flex items-center justify-center p-2 rounded-md text-gray-400 hover:text-gray-300 hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-inset focus:ring-blue-500"
            >
              {isOpen ? (
                <XMarkIcon className="block h-6 w-6" />
              ) : (
                <Bars3Icon className="block h-6 w-6" />
              )}
            </button>
          </div>
        </div>
      </div>

      {/* Mobile menu */}
      <div className={`sm:hidden ${isOpen ? 'block' : 'hidden'}`}>
        <div className="pt-2 pb-3 space-y-1">
          {filteredNavigation.map((item) => {
            const isActive = pathname === item.href;
            return (
              <Link
                key={item.name}
                href={item.href}
                className={`block pl-3 pr-4 py-2 border-l-4 text-base font-medium ${
                  isActive
                    ? 'bg-blue-900 border-blue-500 text-blue-300'
                    : 'border-transparent text-gray-300 hover:bg-gray-700 hover:border-gray-300 hover:text-gray-200'
                }`}
                onClick={() => setIsOpen(false)}
              >
                <div className="flex items-center">
                  <item.icon className="w-5 h-5 mr-3" />
                  {item.name}
                </div>
              </Link>
            );
          })}
        </div>

        {/* Mobile user menu */}
        {!isLoading && (
          <div className="pt-4 pb-3 border-t border-gray-700">
            {user ? (
              <div className="space-y-1">
                <div className="px-4 py-2">
                  <p className="text-base font-medium text-gray-200">
                    {user.first_name || user.username}
                  </p>
                  <p className="text-sm text-gray-400">{user.email}</p>
                </div>
                <Link
                  href="/profile"
                  className="block px-4 py-2 text-base font-medium text-gray-300 hover:text-gray-200 hover:bg-gray-700"
                  onClick={() => setIsOpen(false)}
                >
                  Profile
                </Link>
                <button
                  onClick={() => {
                    handleLogout();
                    setIsOpen(false);
                  }}
                  className="block w-full text-left px-4 py-2 text-base font-medium text-gray-300 hover:text-gray-200 hover:bg-gray-700"
                >
                  Logout
                </button>
              </div>
            ) : (
              <div className="space-y-1">
                <Link
                  href="/login"
                  className="block px-4 py-2 text-base font-medium text-gray-300 hover:text-gray-200 hover:bg-gray-700"
                  onClick={() => setIsOpen(false)}
                >
                  Login
                </Link>
                <Link
                  href="/register"
                  className="block px-4 py-2 text-base font-medium text-gray-300 hover:text-gray-200 hover:bg-gray-700"
                  onClick={() => setIsOpen(false)}
                >
                  Register
                </Link>
              </div>
            )}
          </div>
        )}
      </div>
    </nav>
  );
}