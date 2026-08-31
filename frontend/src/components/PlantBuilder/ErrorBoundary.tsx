import { Component } from 'react';
import type { ErrorInfo, ReactNode } from 'react';
import { AlertTriangle, RefreshCcw } from 'lucide-react';

interface Props {
  children?: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

export class ErrorBoundary extends Component<Props, State> {
  public state: State = {
    hasError: false,
    error: null
  };

  public static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('Uncaught error:', error, errorInfo);
  }

  public render() {
    if (this.state.hasError) {
      return (
        <div className="flex-1 flex flex-col items-center justify-center bg-industrial-900 text-gray-200 p-8">
            <AlertTriangle className="w-16 h-16 text-red-500 mb-4 opacity-80" />
            <h2 className="text-xl font-bold tracking-widest text-white mb-2 uppercase">Rendering Error</h2>
            <p className="text-sm text-gray-400 max-w-md text-center mb-6">
                Plant Builder encountered an unexpected UI error. Your plant data has been preserved in the persistent state.
            </p>
            <div className="bg-industrial-800 border border-red-900/50 rounded p-4 mb-6 w-full max-w-2xl overflow-auto text-xs font-mono text-red-400">
                {this.state.error?.toString()}
            </div>
            <button 
                onClick={() => {
                    this.setState({ hasError: false, error: null });
                }}
                className="flex items-center px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white font-bold rounded shadow-lg transition-colors"
            >
                <RefreshCcw className="w-4 h-4 mr-2" />
                RECOVER EDITOR
            </button>
        </div>
      );
    }

    return this.props.children;
  }
}
