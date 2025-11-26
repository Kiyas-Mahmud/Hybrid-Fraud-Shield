"use client";

import { useRouter } from "next/navigation";
import { FormEvent, useState } from "react";
import toast, { Toaster } from "react-hot-toast";

export default function LoginPage() {
  const router = useRouter();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setLoading(true);

    try {
      const formData = new URLSearchParams();
      formData.append("username", username);
      formData.append("password", password);

      console.log("Attempting login...");
      const response = await fetch("http://localhost:8000/api/v1/auth/login", {
        method: "POST",
        headers: {
          "Content-Type": "application/x-www-form-urlencoded",
        },
        body: formData,
      });

      console.log("Response status:", response.status);
      const data = await response.json();
      console.log("Response data:", data);

      if (!response.ok) {
        console.error("Login failed:", data);
        toast.error(data.detail || "Invalid credentials. Please try again.");
        setLoading(false);
        return;
      }

      // Check if user is admin
      if (data.role !== "SUPER_ADMIN" && data.role !== "ADMIN") {
        console.error("Not an admin user:", data.role);
        toast.error("Access denied. Admin privileges required.");
        setLoading(false);
        return;
      }

      // Store token and user info
      console.log("Storing token and user data...");
      localStorage.setItem("admin_token", data.access_token);
      localStorage.setItem("admin_user", JSON.stringify(data));

      toast.success("Login successful! Redirecting...");

      // Redirect to dashboard
      setTimeout(() => {
        router.push("/admin/dashboard");
      }, 500);
    } catch (err: unknown) {
      console.error("Login error:", err);
      const message =
        err instanceof Error
          ? err.message
          : "Login failed. Please check your connection.";
      toast.error(message);
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-primary-navy via-gray-900 to-primary-navy">
      <Toaster
        position="top-right"
        toastOptions={{
          success: {
            style: {
              background: "#34B1AA",
              color: "white",
              fontWeight: "500",
            },
            iconTheme: {
              primary: "white",
              secondary: "#34B1AA",
            },
          },
          error: {
            style: {
              background: "#ef4444",
              color: "white",
              fontWeight: "500",
            },
            iconTheme: {
              primary: "white",
              secondary: "#ef4444",
            },
          },
        }}
      />
      <div className="bg-white p-10 rounded-2xl shadow-2xl w-full max-w-md">
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-br from-primary-orange to-yellow-500 rounded-2xl mb-4 shadow-lg">
            <span className="text-white text-2xl font-bold">FS</span>
          </div>
          <h1 className="text-3xl font-bold text-primary-navy mb-2">
            Fraud Shield
          </h1>
          <p className="text-admin-text-light font-medium">
            Admin Dashboard Login
          </p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-5">
          <div>
            <label
              htmlFor="username"
              className="block text-sm font-semibold text-primary-navy mb-2"
            >
              Username
            </label>
            <input
              type="text"
              id="username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className="w-full px-4 py-3 border-2 border-gray-200 rounded-lg text-primary-navy focus:outline-none focus:border-primary-orange transition-all"
              placeholder="Enter your username"
              required
            />
          </div>

          <div>
            <label
              htmlFor="password"
              className="block text-sm font-semibold text-primary-navy mb-2"
            >
              Password
            </label>
            <input
              type="password"
              id="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full px-4 py-3 border-2 border-gray-200 rounded-lg text-primary-navy focus:outline-none focus:border-primary-orange transition-all"
              placeholder="Enter your password"
              required
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-gradient-to-r from-primary-orange to-yellow-500 hover:from-yellow-500 hover:to-primary-orange text-white font-bold py-3.5 rounded-lg transition-all duration-300 shadow-lg hover:shadow-xl disabled:opacity-50 disabled:cursor-not-allowed transform hover:scale-[1.02]"
          >
            {loading ? "Signing in..." : "Sign In"}
          </button>
        </form>

        <div className="mt-6 text-center text-sm text-admin-text-light">
          Demo: <span className="font-semibold text-primary-navy">admin</span> /{" "}
          <span className="font-semibold text-primary-navy">admin123</span>
        </div>
      </div>
    </div>
  );
}
