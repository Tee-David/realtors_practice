"use client";

import { useEffect, useState } from "react";
import { cn } from "@/lib/utils";

interface TypewriterEffectProps {
  words: Array<{
    text: string;
    className?: string;
  }>;
  className?: string;
  cursorClassName?: string;
}

export const TypewriterEffect = ({
  words,
  className,
  cursorClassName,
}: TypewriterEffectProps) => {
  const [currentWordIndex, setCurrentWordIndex] = useState(0);
  const [currentText, setCurrentText] = useState("");
  const [isDeleting, setIsDeleting] = useState(false);

  useEffect(() => {
    const currentWord = words[currentWordIndex].text;
    const typingSpeed = isDeleting ? 50 : 100;
    const pauseTime = 2000;

    const timeout = setTimeout(() => {
      if (!isDeleting && currentText === currentWord) {
        // Finished typing, pause then start deleting
        setTimeout(() => setIsDeleting(true), pauseTime);
      } else if (isDeleting && currentText === "") {
        // Finished deleting, move to next word
        setIsDeleting(false);
        setCurrentWordIndex((prev) => (prev + 1) % words.length);
      } else {
        // Continue typing or deleting
        setCurrentText(
          isDeleting
            ? currentWord.substring(0, currentText.length - 1)
            : currentWord.substring(0, currentText.length + 1)
        );
      }
    }, typingSpeed);

    return () => clearTimeout(timeout);
  }, [currentText, isDeleting, currentWordIndex, words]);

  return (
    <div className={cn("inline-flex items-center", className)}>
      <span className={words[currentWordIndex].className}>
        {currentText}
      </span>
      <span
        className={cn(
          "inline-block w-[3px] h-5 ml-1 bg-blue-400 animate-pulse",
          cursorClassName
        )}
      />
    </div>
  );
};
