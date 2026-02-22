import { BrowserRouter as Router, Routes, Route, Link, useLocation } from 'react-router-dom';
import { Shield, Settings } from 'lucide-react';
import Home from './pages/Home';
import Admin from './pages/Admin';

function Navigation() {
  const location = useLocation();

  return (
    <nav className="bg-brand-navy sticky top-0 z-50 shadow-md border-b border-slate-800">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          <div className="flex">
            <Link to="/" className="flex items-center gap-2">
              <Shield className="w-8 h-8 text-brand-emerald" />
              <span className="text-xl font-bold text-white tracking-wide">
                FraudGuard
              </span>
            </Link>
          </div>

          <div className="flex items-center space-x-4">
            <Link
              to="/"
              className={`px-3 py-2 rounded-md text-sm font-medium transition-colors ${location.pathname === '/'
                ? 'bg-slate-800 text-brand-emerald'
                : 'text-slate-300 hover:text-white hover:bg-slate-800'
                }`}
            >
              Scanner
            </Link>
            <Link
              to="/admin"
              className={`flex items-center gap-1.5 px-3 py-2 rounded-md text-sm font-medium transition-colors ${location.pathname === '/admin'
                ? 'bg-slate-800 text-brand-emerald'
                : 'text-slate-300 hover:text-white hover:bg-slate-800'
                }`}
            >
              <Settings className="w-4 h-4" />
              Rules Config
            </Link>
          </div>
        </div>
      </div>
    </nav>
  );
}

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-brand-offwhite flex flex-col font-sans">
        <Navigation />
        <main className="flex-1 px-4 sm:px-6 lg:px-8 py-8 w-full max-w-7xl mx-auto">
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/admin" element={<Admin />} />
          </Routes>
        </main>

        <footer className="bg-white border-t border-slate-200 mt-auto py-8">
          <div className="max-w-7xl mx-auto px-4 text-center text-sm text-slate-500">
            <p>Built By Mayank Sahu • Digital Fraud Awareness Platform</p>
          </div>
        </footer>
      </div>
    </Router>
  );
}

export default App;
