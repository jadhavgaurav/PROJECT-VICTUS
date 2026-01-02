import React, { forwardRef } from 'react';
import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

interface TextFieldProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label: string;
  error?: string;
  helperText?: string;
  endAdornment?: React.ReactNode;
}

export const TextField = forwardRef<HTMLInputElement, TextFieldProps>(
  ({ label, error, helperText, className, id, endAdornment, ...props }, ref) => {
    return (
      <div className="space-y-1">
        <label htmlFor={id} className="block text-sm font-medium leading-6 text-gray-300">
          {label}
        </label>
        <div className="relative rounded-xl shadow-sm">
          <input
            ref={ref}
            id={id}
            className={twMerge(
              clsx(
                "block w-full rounded-xl border border-gray-800 bg-gray-950 py-3 px-4 text-white shadow-sm placeholder:text-gray-500 focus:outline-none focus:ring-2 sm:text-sm sm:leading-6 transition-colors duration-200",
                error
                  ? "border-red-500/50 ring-red-500/20 focus:ring-red-500 focus:border-red-500"
                  : "focus:ring-indigo-500/50 focus:border-indigo-500 hover:border-gray-700",
                  className
              )
            )}
            aria-invalid={!!error}
            aria-describedby={error ? `${id}-error` : helperText ? `${id}-helper` : undefined}
            {...props}
          />
          {endAdornment && (
            <div className="absolute inset-y-0 right-0 flex items-center pr-3">
              {endAdornment}
            </div>
          )}
        </div>
        {error ? (
          <p className="mt-1 text-sm text-red-600 animate-in slide-in-from-top-1" id={`${id}-error`}>
            {error}
          </p>
        ) : helperText ? (
          <p className="mt-1 text-sm text-gray-500" id={`${id}-helper`}>
            {helperText}
          </p>
        ) : null}
      </div>
    );
  }
);
