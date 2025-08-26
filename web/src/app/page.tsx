import Link from 'next/link';
import { 
  MagnifyingGlassIcon, 
  DocumentTextIcon, 
  CloudArrowUpIcon,
  ChartBarIcon 
} from '@heroicons/react/24/outline';

export default function Home() {
  return (
    <div className="bg-gray-900">
      {/* Hero Section */}
      <div className="relative gradient-bg">
        <div className="absolute inset-0 bg-gray-900 bg-opacity-40"></div>
        <div className="relative max-w-7xl mx-auto py-24 px-4 sm:py-32 sm:px-6 lg:px-8">
          <h1 className="text-4xl font-extrabold tracking-tight text-white sm:text-5xl lg:text-6xl">
            SailorBob FOIA Portal
          </h1>
          <p className="mt-6 text-xl text-blue-100 max-w-3xl">
            Access Freedom of Information Act documents with powerful search capabilities. 
            Discover government transparency through our comprehensive document archive.
          </p>
          <div className="mt-10">
            <Link
              href="/search"
              className="inline-flex items-center px-6 py-3 border border-transparent text-base font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 transition-colors"
            >
              <MagnifyingGlassIcon className="w-5 h-5 mr-2" />
              Start Searching
            </Link>
          </div>
        </div>
      </div>

      {/* Features Section */}
      <div className="py-16 bg-gray-800">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <h2 className="text-3xl font-extrabold text-white">
              Powerful Document Discovery
            </h2>
            <p className="mt-4 text-lg text-gray-300">
              Advanced features to help you find and access FOIA documents efficiently
            </p>
          </div>

          <div className="mt-16">
            <div className="grid grid-cols-1 gap-8 sm:grid-cols-2 lg:grid-cols-4">
              <div className="card p-6 text-center">
                <div className="w-12 h-12 mx-auto bg-blue-600 rounded-lg flex items-center justify-center">
                  <MagnifyingGlassIcon className="w-6 h-6 text-white" />
                </div>
                <h3 className="mt-4 text-lg font-medium text-white">Full-Text Search</h3>
                <p className="mt-2 text-sm text-gray-400">
                  Search through document content with advanced filtering and faceted navigation
                </p>
              </div>

              <div className="card p-6 text-center">
                <div className="w-12 h-12 mx-auto bg-green-600 rounded-lg flex items-center justify-center">
                  <DocumentTextIcon className="w-6 h-6 text-white" />
                </div>
                <h3 className="mt-4 text-lg font-medium text-white">OCR Processing</h3>
                <p className="mt-2 text-sm text-gray-400">
                  Automatic text extraction from PDFs and scanned documents using OCR technology
                </p>
              </div>

              <div className="card p-6 text-center">
                <div className="w-12 h-12 mx-auto bg-purple-600 rounded-lg flex items-center justify-center">
                  <CloudArrowUpIcon className="w-6 h-6 text-white" />
                </div>
                <h3 className="mt-4 text-lg font-medium text-white">Easy Upload</h3>
                <p className="mt-2 text-sm text-gray-400">
                  Streamlined document upload with automatic metadata extraction and categorization
                </p>
              </div>

              <div className="card p-6 text-center">
                <div className="w-12 h-12 mx-auto bg-yellow-600 rounded-lg flex items-center justify-center">
                  <ChartBarIcon className="w-6 h-6 text-white" />
                </div>
                <h3 className="mt-4 text-lg font-medium text-white">Analytics</h3>
                <p className="mt-2 text-sm text-gray-400">
                  Track document usage and search patterns with comprehensive analytics
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Stats Section */}
      <div className="bg-gray-900 py-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <h2 className="text-3xl font-extrabold text-white">
              Growing Document Archive
            </h2>
            <p className="mt-4 text-lg text-gray-300">
              Our collection continues to expand with new FOIA releases
            </p>
          </div>

          <div className="mt-12 grid grid-cols-1 gap-8 sm:grid-cols-2 lg:grid-cols-4">
            <div className="text-center">
              <div className="text-4xl font-bold text-blue-400">1,250+</div>
              <div className="mt-2 text-sm text-gray-400">Documents</div>
            </div>
            <div className="text-center">
              <div className="text-4xl font-bold text-green-400">45+</div>
              <div className="mt-2 text-sm text-gray-400">Agencies</div>
            </div>
            <div className="text-center">
              <div className="text-4xl font-bold text-purple-400">2.3GB</div>
              <div className="mt-2 text-sm text-gray-400">Total Size</div>
            </div>
            <div className="text-center">
              <div className="text-4xl font-bold text-yellow-400">15,000+</div>
              <div className="mt-2 text-sm text-gray-400">Searches</div>
            </div>
          </div>
        </div>
      </div>

      {/* Recent Documents Section */}
      <div className="bg-gray-800 py-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between">
            <h2 className="text-3xl font-extrabold text-white">
              Recently Added Documents
            </h2>
            <Link
              href="/documents"
              className="text-blue-400 hover:text-blue-300 font-medium"
            >
              View all →
            </Link>
          </div>

          <div className="mt-8 grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
            {/* Placeholder for recent documents */}
            {[1, 2, 3].map((i) => (
              <div key={i} className="document-card">
                <h3 className="text-lg font-medium text-white mb-2">
                  Sample Document Title {i}
                </h3>
                <p className="text-sm text-gray-400 mb-3">
                  Lorem ipsum dolor sit amet, consectetur adipiscing elit. 
                  Sed do eiusmod tempor incididunt ut labore.
                </p>
                <div className="flex items-center justify-between text-xs text-gray-500">
                  <span>Department of Defense</span>
                  <span>2 days ago</span>
                </div>
                <div className="mt-3 flex flex-wrap gap-1">
                  <span className="tag-pill">Military</span>
                  <span className="tag-pill">Classified</span>
                </div>
              </div>
            ))}
          </div>

          <div className="mt-8 text-center">
            <Link
              href="/search"
              className="btn-primary"
            >
              Search All Documents
            </Link>
          </div>
        </div>
      </div>

      {/* Footer */}
      <footer className="bg-gray-900 border-t border-gray-700">
        <div className="max-w-7xl mx-auto py-12 px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div>
              <h3 className="text-lg font-semibold text-white mb-4">
                SailorBob FOIA Portal
              </h3>
              <p className="text-gray-400 text-sm">
                Promoting government transparency through accessible FOIA document archives.
              </p>
            </div>
            <div>
              <h4 className="text-md font-medium text-white mb-4">Quick Links</h4>
              <ul className="space-y-2">
                <li><Link href="/search" className="text-gray-400 hover:text-gray-300 text-sm">Search Documents</Link></li>
                <li><Link href="/documents" className="text-gray-400 hover:text-gray-300 text-sm">Browse Archive</Link></li>
                <li><Link href="/about" className="text-gray-400 hover:text-gray-300 text-sm">About</Link></li>
                <li><Link href="/contact" className="text-gray-400 hover:text-gray-300 text-sm">Contact</Link></li>
              </ul>
            </div>
            <div>
              <h4 className="text-md font-medium text-white mb-4">Resources</h4>
              <ul className="space-y-2">
                <li><Link href="/api/docs" className="text-gray-400 hover:text-gray-300 text-sm">API Documentation</Link></li>
                <li><Link href="/help" className="text-gray-400 hover:text-gray-300 text-sm">Help & Support</Link></li>
                <li><Link href="/privacy" className="text-gray-400 hover:text-gray-300 text-sm">Privacy Policy</Link></li>
                <li><Link href="/terms" className="text-gray-400 hover:text-gray-300 text-sm">Terms of Service</Link></li>
              </ul>
            </div>
          </div>
          <div className="mt-8 pt-8 border-t border-gray-700 text-center">
            <p className="text-gray-400 text-sm">
              © 2025 SailorBob FOIA Portal. All rights reserved.
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
}
