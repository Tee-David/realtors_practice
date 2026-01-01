"use client";
import { ReactNode, useMemo } from "react";
import { motion } from "framer-motion";
import { cn } from "@/lib/utils";

interface LoaderProps {
  children?: ReactNode;
  className?: string;
  variant?: "default" | "cube" | "dual-ring" | "magnetic-dots";
  size?: number;
}

export function Loader({
  children,
  className = "",
  variant = "dual-ring",
  size,
}: LoaderProps) {
  const finalSize = useMemo(() => size ?? 48, [size]);

  return (
    <div className={cn("flex flex-col items-center justify-center gap-4", className)}>
      <div
        className="relative flex items-center justify-center"
        style={{
          height: finalSize,
          width: finalSize,
        }}
      >
        {variant === "default" && (
          <>
            <div className="absolute inset-0 rounded-full border-t-[3px] border-b-[3px] border-blue-500/30" />
            <motion.div
              className="absolute inset-0 rounded-full border-t-[3px] border-b-[3px] border-blue-500"
              animate={{ rotate: 360 }}
              transition={{ repeat: Infinity, duration: 1, ease: "linear" }}
            />
          </>
        )}

        {variant === "cube" && (
          <motion.div
            className="absolute inset-0 bg-blue-500 shadow-[0_0_8px_rgba(59,130,246,0.6)]"
            animate={{ rotateX: [0, 180, 0], rotateY: [0, 180, 0] }}
            transition={{ repeat: Infinity, duration: 1.1, ease: "linear" }}
          />
        )}

        {variant === "dual-ring" && (
          <>
            <div className="absolute inset-0 rounded-full border-[3px] border-blue-500/20" />
            <motion.div
              className="absolute inset-0 rounded-full border-t-[3px] border-blue-500 border-r-transparent border-b-transparent border-l-transparent"
              animate={{ rotate: 360 }}
              transition={{ repeat: Infinity, duration: 1, ease: "linear" }}
            />
            <motion.div
              className="absolute inset-[20%] rounded-full border-[3px] border-blue-400/30"
              animate={{ rotate: -360 }}
              transition={{ repeat: Infinity, duration: 0.8, ease: "linear" }}
            />
            <motion.div
              className="absolute inset-[20%] rounded-full border-b-[3px] border-blue-400 border-t-transparent border-r-transparent border-l-transparent"
              animate={{ rotate: -360 }}
              transition={{ repeat: Infinity, duration: 0.8, ease: "linear" }}
            />
          </>
        )}

        {variant === "magnetic-dots" && (
          <div className="relative flex items-center justify-center h-full w-full">
            <motion.div
              className="absolute rounded-full bg-blue-500"
              style={{
                height: finalSize / 3,
                width: finalSize / 3,
              }}
              animate={{ x: [-(finalSize / 3), 0, -(finalSize / 3)] }}
              transition={{
                repeat: Infinity,
                duration: 1.2,
                ease: "easeInOut",
                times: [0, 0.5, 1],
              }}
            />
            <motion.div
              className="absolute rounded-full bg-blue-400"
              style={{
                height: finalSize / 3,
                width: finalSize / 3,
              }}
              animate={{ x: [finalSize / 3, 0, finalSize / 3] }}
              transition={{
                repeat: Infinity,
                duration: 1.2,
                ease: "easeInOut",
                times: [0, 0.5, 1],
              }}
            />
            <motion.div
              className="absolute rounded-full bg-blue-600 opacity-0"
              style={{
                height: finalSize / 3,
                width: finalSize / 3,
              }}
              animate={{ opacity: [0, 1, 0] }}
              transition={{
                repeat: Infinity,
                duration: 1.2,
                ease: "easeInOut",
                times: [0.45, 0.5, 0.55],
              }}
            />
          </div>
        )}
      </div>

      {children && (
        <div className="text-sm text-slate-400 dark:text-slate-400 animate-pulse">
          {children}
        </div>
      )}
    </div>
  );
}
