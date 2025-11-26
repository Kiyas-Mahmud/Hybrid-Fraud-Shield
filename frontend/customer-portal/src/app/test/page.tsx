'use client';

export default function TestPage() {
  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center">
      <div className="text-center">
        <h1 className="text-4xl font-bold text-gray-900 mb-4">
          ✅ Next.js is Working!
        </h1>
        <p className="text-gray-600 mb-8">
          If you can see this, the frontend is running correctly.
        </p>
        <div className="space-y-4">
          <a 
            href="/login" 
            className="block bg-blue-500 text-white px-6 py-3 rounded-lg hover:bg-blue-600"
          >
            Go to Login Page
          </a>
          <a 
            href="/register" 
            className="block bg-green-500 text-white px-6 py-3 rounded-lg hover:bg-green-600"
          >
            Go to Register Page
          </a>
        </div>
      </div>
    </div>
  );
}
