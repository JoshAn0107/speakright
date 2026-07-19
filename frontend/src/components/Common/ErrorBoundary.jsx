import { Component } from 'react';

// 渲染出错时显示提示而不是整页白屏
class ErrorBoundary extends Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError() {
    return { hasError: true };
  }

  componentDidCatch(error, info) {
    console.error('Render error:', error, info);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="max-w-md mx-auto mt-16 p-6 bg-red-50 border border-red-200 rounded-xl text-center">
          <p className="text-red-700 font-medium mb-2">页面出了点问题</p>
          <p className="text-sm text-gray-600 mb-4">请刷新页面重试；如果反复出现请联系老师反馈</p>
          <button
            onClick={() => window.location.reload()}
            className="px-6 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700"
          >
            刷新页面
          </button>
        </div>
      );
    }
    return this.props.children;
  }
}

export default ErrorBoundary;
