import { useState, useCallback, useMemo } from "react";

export interface UsePaginationOptions {
  initialPage?: number;
  itemsPerPage?: number;
  total?: number;
}

/**
 * Custom hook for managing pagination state and controls
 */
export function usePagination(options: UsePaginationOptions = {}) {
  const { initialPage = 1, itemsPerPage = 20, total = 0 } = options;

  const [currentPage, setCurrentPage] = useState(initialPage);

  // Calculate pagination values
  const totalPages = useMemo(
    () => Math.max(1, Math.ceil(total / itemsPerPage)),
    [total, itemsPerPage]
  );

  const offset = useMemo(
    () => (currentPage - 1) * itemsPerPage,
    [currentPage, itemsPerPage]
  );

  const startIndex = useMemo(() => offset + 1, [offset]);

  const endIndex = useMemo(
    () => Math.min(offset + itemsPerPage, total),
    [offset, itemsPerPage, total]
  );

  const hasNextPage = useMemo(
    () => currentPage < totalPages,
    [currentPage, totalPages]
  );

  const hasPrevPage = useMemo(() => currentPage > 1, [currentPage]);

  // Navigation functions
  const goToPage = useCallback(
    (page: number) => {
      const validPage = Math.max(1, Math.min(page, totalPages));
      setCurrentPage(validPage);
    },
    [totalPages]
  );

  const nextPage = useCallback(() => {
    if (hasNextPage) {
      setCurrentPage((prev) => prev + 1);
    }
  }, [hasNextPage]);

  const prevPage = useCallback(() => {
    if (hasPrevPage) {
      setCurrentPage((prev) => prev - 1);
    }
  }, [hasPrevPage]);

  const goToFirstPage = useCallback(() => {
    setCurrentPage(1);
  }, []);

  const goToLastPage = useCallback(() => {
    setCurrentPage(totalPages);
  }, [totalPages]);

  // Reset pagination (useful when filters change)
  const reset = useCallback(() => {
    setCurrentPage(initialPage);
  }, [initialPage]);

  // Get page numbers for pagination UI (with ellipsis)
  const getPageNumbers = useCallback(
    (maxVisible: number = 5) => {
      const pages: (number | string)[] = [];

      if (totalPages <= maxVisible) {
        // Show all pages if total is small
        for (let i = 1; i <= totalPages; i++) {
          pages.push(i);
        }
      } else {
        // Show pages with ellipsis
        const sidePages = Math.floor((maxVisible - 3) / 2);

        if (currentPage <= sidePages + 2) {
          // Near the start
          for (let i = 1; i <= maxVisible - 2; i++) {
            pages.push(i);
          }
          pages.push("...");
          pages.push(totalPages);
        } else if (currentPage >= totalPages - sidePages - 1) {
          // Near the end
          pages.push(1);
          pages.push("...");
          for (let i = totalPages - (maxVisible - 3); i <= totalPages; i++) {
            pages.push(i);
          }
        } else {
          // In the middle
          pages.push(1);
          pages.push("...");
          for (
            let i = currentPage - sidePages;
            i <= currentPage + sidePages;
            i++
          ) {
            pages.push(i);
          }
          pages.push("...");
          pages.push(totalPages);
        }
      }

      return pages;
    },
    [currentPage, totalPages]
  );

  return {
    // State
    currentPage,
    totalPages,
    itemsPerPage,
    offset,
    startIndex,
    endIndex,
    hasNextPage,
    hasPrevPage,

    // Actions
    goToPage,
    nextPage,
    prevPage,
    goToFirstPage,
    goToLastPage,
    reset,
    getPageNumbers,
  };
}
