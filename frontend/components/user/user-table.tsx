"use client";

import {
  Edit,
  Trash2,
  RotateCcw,
  MoreVertical,
  Mail,
  User as UserIcon,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import type { User } from "@/lib/types";
import { getRoleColor, getStatusColor } from "@/lib/utils";
import { toast } from "sonner";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";

interface UserTableProps {
  users: User[];
  onEdit: (user: User) => void;
  onDelete: (userId: string) => void;
  onToggleStatus: (userId: string) => void;
}

export function UserTable({
  users,
  onEdit,
  onDelete,
  onToggleStatus,
}: UserTableProps) {
  const handleDelete = (user: User) => {
    if (window.confirm(`Are you sure you want to delete ${user.name}?`)) {
      onDelete(user.id);
      toast.success("User deleted successfully");
    }
  };

  const handleToggleStatus = (user: User) => {
    onToggleStatus(user.id);
    toast.success(
      `User ${
        user.status === "Active" ? "deactivated" : "activated"
      } successfully`
    );
  };

  if (users.length === 0) {
    return (
      <div className="bg-slate-800 rounded-lg border border-slate-700 p-8 text-center">
        <p className="text-slate-400">No users found</p>
      </div>
    );
  }

  return (
    <div className="bg-slate-800 rounded-lg border border-slate-700 overflow-hidden">
      {/* Mobile Card View */}
      <div className="block sm:hidden">
        <div className="divide-y divide-slate-700">
          {users.map((user) => (
            <div key={user.id} className="p-4 space-y-3">
              <div className="flex items-start justify-between">
                <div className="flex items-center space-x-3 flex-1 min-w-0">
                  <div className="w-10 h-10 bg-slate-700 rounded-full flex items-center justify-center flex-shrink-0">
                    <UserIcon className="w-5 h-5 text-slate-400" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-white font-medium truncate">
                      {user.name}
                    </p>
                    <div className="flex items-center space-x-1 mt-1">
                      <Mail className="w-3 h-3 text-slate-400" />
                      <p className="text-slate-400 text-sm truncate">
                        {user.email}
                      </p>
                    </div>
                  </div>
                </div>

                <DropdownMenu>
                  <DropdownMenuTrigger asChild>
                    <Button variant="ghost" size="sm" className="h-8 w-8 p-0">
                      <MoreVertical className="w-4 h-4 text-white" />
                    </Button>
                  </DropdownMenuTrigger>
                  <DropdownMenuContent
                    align="end"
                    className="bg-slate-700 border-slate-600"
                  >
                    <DropdownMenuItem
                      onClick={() => onEdit(user)}
                      className="text-slate-300 focus:bg-slate-600"
                    >
                      <Edit className="w-4 h-4 mr-2" />
                      Edit
                    </DropdownMenuItem>
                    <DropdownMenuItem
                      onClick={() => handleToggleStatus(user)}
                      className="text-slate-300 focus:bg-slate-600"
                    >
                      <RotateCcw className="w-4 h-4 mr-2" />
                      {user.status === "Active" ? "Deactivate" : "Activate"}
                    </DropdownMenuItem>
                    <DropdownMenuItem
                      onClick={() => handleDelete(user)}
                      className="text-red-400 focus:bg-red-500/10"
                    >
                      <Trash2 className="w-4 h-4 mr-2" />
                      Delete
                    </DropdownMenuItem>
                  </DropdownMenuContent>
                </DropdownMenu>
              </div>

              <div className="grid grid-cols-2 gap-3 text-sm">
                <div>
                  <span className="text-slate-400 text-xs uppercase tracking-wider">
                    Role
                  </span>
                  <div className="mt-1">
                    <span
                      className={`px-2 py-1 rounded-full text-xs font-medium ${getRoleColor(
                        user.role
                      )}`}
                    >
                      {user.role}
                    </span>
                  </div>
                </div>
                <div>
                  <span className="text-slate-400 text-xs uppercase tracking-wider">
                    Status
                  </span>
                  <div className="mt-1">
                    <span
                      className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(
                        user.status
                      )}`}
                    >
                      {user.status}
                    </span>
                  </div>
                </div>
              </div>

              <div>
                <span className="text-slate-400 text-xs uppercase tracking-wider">
                  Last Login
                </span>
                <p className="text-slate-300 text-sm mt-1">{user.lastLogin}</p>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Desktop Table View */}
      <div className="hidden sm:block overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr className="border-b border-slate-700 bg-slate-900/50">
              <th className="text-left p-4 text-sm font-medium text-slate-400">
                NAME
              </th>
              <th className="text-left p-4 text-sm font-medium text-slate-400">
                ROLE
              </th>
              <th className="text-left p-4 text-sm font-medium text-slate-400">
                STATUS
              </th>
              <th className="text-left p-4 text-sm font-medium text-slate-400">
                LAST LOGIN
              </th>
              <th className="text-right p-4 text-sm font-medium text-slate-400">
                ACTIONS
              </th>
            </tr>
          </thead>
          <tbody>
            {users.map((user) => (
              <tr
                key={user.id}
                className="border-b border-slate-700 hover:bg-slate-700/30 transition-colors"
              >
                <td className="p-4">
                  <div className="flex items-center space-x-3">
                    <div className="w-8 h-8 bg-slate-700 rounded-full flex items-center justify-center flex-shrink-0">
                      <UserIcon className="w-4 h-4 text-slate-400" />
                    </div>
                    <div className="min-w-0">
                      <p className="text-white font-medium truncate">
                        {user.name}
                      </p>
                      <p className="text-slate-400 text-sm truncate">
                        {user.email}
                      </p>
                    </div>
                  </div>
                </td>
                <td className="p-4">
                  <span
                    className={`px-2 py-1 rounded-full text-xs font-medium ${getRoleColor(
                      user.role
                    )}`}
                  >
                    {user.role}
                  </span>
                </td>
                <td className="p-4">
                  <span
                    className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(
                      user.status
                    )}`}
                  >
                    {user.status}
                  </span>
                </td>
                <td className="p-4 text-slate-300 text-sm">{user.lastLogin}</td>
                <td className="p-4">
                  <div className="flex items-center justify-end space-x-2">
                    <Button
                      onClick={() => onEdit(user)}
                      variant="ghost"
                      size="sm"
                      className="text-white hover:text-blue-400 hover:bg-blue-500/10"
                      title="Edit user"
                    >
                      <Edit className="w-4 h-4" />
                    </Button>
                    <Button
                      onClick={() => handleToggleStatus(user)}
                      variant="ghost"
                      size="sm"
                      className="text-white hover:text-yellow-400 hover:bg-yellow-500/10"
                      title={
                        user.status === "Active"
                          ? "Deactivate user"
                          : "Activate user"
                      }
                    >
                      <RotateCcw className="w-4 h-4" />
                    </Button>
                    <Button
                      onClick={() => handleDelete(user)}
                      variant="ghost"
                      size="sm"
                      className="text-white hover:text-red-400 hover:bg-red-500/10"
                      title="Delete user"
                    >
                      <Trash2 className="w-4 h-4" />
                    </Button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
