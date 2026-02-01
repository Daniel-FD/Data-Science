import React from 'react';

interface State { hasError: boolean; error?: Error }

class ErrorBoundaryInner extends React.Component<{children: React.ReactNode; pathname: string}, State> {
  constructor(props: {children: React.ReactNode; pathname: string}) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  componentDidUpdate(prevProps: {pathname: string}) {
    if (this.state.hasError && prevProps.pathname !== this.props.pathname) {
      this.setState({ hasError: false, error: undefined });
    }
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="mx-auto max-w-lg py-20 text-center">
          <div className="text-5xl mb-4">&#x26A0;&#xFE0F;</div>
          <h2 className="text-xl font-semibold text-gray-900 mb-2">Algo ha ido mal</h2>
          <p className="text-gray-500 mb-6">Ha ocurrido un error inesperado. Prueba a recargar la pagina.</p>
          <button onClick={() => this.setState({ hasError: false, error: undefined })}
            className="rounded-lg bg-blue-600 px-6 py-2.5 text-sm font-medium text-white hover:bg-blue-700 transition-colors">
            Reintentar
          </button>
        </div>
      );
    }
    return this.props.children;
  }
}

// Wrapper to inject useLocation
import { useLocation } from 'react-router-dom';

export default function ErrorBoundary({ children }: { children: React.ReactNode }) {
  const { pathname } = useLocation();
  return <ErrorBoundaryInner pathname={pathname}>{children}</ErrorBoundaryInner>;
}
