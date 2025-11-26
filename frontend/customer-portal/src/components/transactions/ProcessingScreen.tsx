'use client';

interface ProcessingScreenProps {
  /**
   * Main message to display during processing
   * @default "Analyzing transaction with AI models..."
   */
  message?: string;
  
  /**
   * Optional subtitle/secondary message
   */
  subtitle?: string;
  
  /**
   * Whether to show the pulsing animation
   * @default true
   */
  animate?: boolean;
}

/**
 * Reusable loading/processing screen component
 * 
 * Features:
 * - Animated spinner with pulse effect
 * - Customizable message text
 * - Blue theme matching design system
 * - Full-screen overlay or inline usage
 * 
 * @example
 * // Basic usage
 * <ProcessingScreen />
 * 
 * @example
 * // Custom message
 * <ProcessingScreen 
 *   message="Processing payment..."
 *   subtitle="Please wait while we verify your transaction"
 * />
 */
export default function ProcessingScreen({
  message = "Analyzing transaction with AI models...",
  subtitle,
  animate = true,
}: ProcessingScreenProps) {
  return (
    <div className="min-h-[400px] flex items-center justify-center p-8">
      <div className="text-center space-y-6 max-w-md">
        {/* Animated Spinner */}
        <div className="flex justify-center">
          <div className="relative">
            {/* Outer pulse ring */}
            {animate && (
              <div className="absolute inset-0 rounded-full bg-blue-400 opacity-20 animate-ping" />
            )}
            
            {/* Main spinner */}
            <div className="relative w-20 h-20 rounded-full border-4 border-blue-100 border-t-blue-600 animate-spin" />
            
            {/* Inner glow */}
            <div className="absolute inset-2 rounded-full bg-blue-50" />
          </div>
        </div>

        {/* Message Text */}
        <div className="space-y-2">
          <h2 className="text-xl font-semibold text-gray-900">
            {message}
          </h2>
          
          {subtitle && (
            <p className="text-sm text-gray-600">
              {subtitle}
            </p>
          )}
        </div>

        {/* Progress Indicators */}
        <div className="space-y-2">
          <div className="flex justify-center gap-1.5">
            {[0, 1, 2].map((index) => (
              <div
                key={index}
                className={`h-2 w-2 rounded-full bg-blue-600 ${
                  animate ? 'animate-bounce' : ''
                }`}
                style={{
                  animationDelay: `${index * 0.15}s`,
                }}
              />
            ))}
          </div>
          
          <p className="text-xs text-gray-500">
            This may take a few moments
          </p>
        </div>
      </div>
    </div>
  );
}
