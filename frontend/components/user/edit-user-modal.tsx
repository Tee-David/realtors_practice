"use client";

import type React from "react";
import { useState, useEffect } from "react";
import { X } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import type { User } from "@/lib/types";
import { toast } from "sonner";

interface EditUserModalProps {
  isOpen: boolean;
  onClose: () => void;
  onEdit: (user: User) => void;
  user: User;
}

export function EditUserModal({
  isOpen,
  onClose,
  onEdit,
  user,
}: EditUserModalProps) {
  const [formData, setFormData] = useState({
    name: "",
    email: "",
    role: "Viewer" as User["role"],
    status: "Active" as User["status"],
  });
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    if (user) {
      setFormData({
        name: user.name,
        email: user.email,
        role: user.role,
        status: user.status,
      });
    }
  }, [user]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!formData.name || !formData.email) {
      toast.error("Please fill in all required fields");
      return;
    }

    setIsLoading(true);

    // Simulate API call
    setTimeout(() => {
      const updatedUser: User = {
        ...user,
        ...formData,
      };

      onEdit(updatedUser);
      setIsLoading(false);
      toast.success("User updated successfully");
      onClose();
    }, 1000);
  };

  const handleClose = () => {
    if (!isLoading) {
      onClose();
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div
        className="fixed inset-0 bg-black bg-opacity-50"
        onClick={handleClose}
      />

      <div className="relative bg-slate-800 rounded-lg border border-slate-700 w-full max-w-md max-h-[90vh] overflow-y-auto">
        <div className="flex items-center justify-between p-4 sm:p-6 border-b border-slate-700 sticky top-0 bg-slate-800">
          <h3 className="text-lg font-semibold text-white">Edit User</h3>
          <button
            onClick={handleClose}
            className="text-slate-400 hover:text-white p-1 rounded"
            disabled={isLoading}
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-4 sm:p-6 space-y-4">
          <div>
            <label className="block text-sm font-medium text-slate-300 mb-2">
              Full Name *
            </label>
            <Input
              type="text"
              value={formData.name}
              onChange={(e) =>
                setFormData({ ...formData, name: e.target.value })
              }
              placeholder="Enter full name"
              className="bg-slate-700 border-slate-600 text-white"
              disabled={isLoading}
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-300 mb-2">
              Email Address *
            </label>
            <Input
              type="email"
              value={formData.email}
              onChange={(e) =>
                setFormData({ ...formData, email: e.target.value })
              }
              placeholder="Enter email address"
              className="bg-slate-700 border-slate-600 text-white"
              disabled={isLoading}
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-300 mb-2">
              Role
            </label>
            <Select
              value={formData.role}
              onValueChange={(value: User["role"]) =>
                setFormData({ ...formData, role: value })
              }
              disabled={isLoading}
            >
              <SelectTrigger className="bg-slate-700 border-slate-600 text-white">
                <SelectValue />
              </SelectTrigger>
              <SelectContent className="bg-slate-700 border-slate-600">
                <SelectItem value="Admin">Admin</SelectItem>
                <SelectItem value="Editor">Editor</SelectItem>
                <SelectItem value="Viewer">Viewer</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-300 mb-2">
              Status
            </label>
            <Select
              value={formData.status}
              onValueChange={(value: User["status"]) =>
                setFormData({ ...formData, status: value })
              }
              disabled={isLoading}
            >
              <SelectTrigger className="bg-slate-700 border-slate-600 text-white">
                <SelectValue />
              </SelectTrigger>
              <SelectContent className="bg-slate-700 border-slate-600">
                <SelectItem value="Active">Active</SelectItem>
                <SelectItem value="Inactive">Inactive</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div className="flex flex-col-reverse sm:flex-row gap-3 pt-4">
            <Button
              type="button"
              variant="outline"
              onClick={handleClose}
              className="border-slate-600 text-slate-300 hover:bg-slate-700 bg-transparent"
              disabled={isLoading}
            >
              Cancel
            </Button>
            <Button
              type="submit"
              className="bg-blue-500 hover:bg-blue-600 text-white"
              disabled={isLoading}
            >
              {isLoading ? "Updating..." : "Update User"}
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
}
