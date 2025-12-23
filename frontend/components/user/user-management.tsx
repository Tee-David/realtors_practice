"use client";

import { useState } from "react";
import { Plus, Search } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { UserTable } from "./user-table";
import { AddUserModal } from "./add-user-modal";
import { EditUserModal } from "./edit-user-modal";
import { mockUsers } from "@/lib/mockData";
import type { User } from "@/lib/types";
import { toast } from "sonner";

export function UserManagement() {
  const [users, setUsers] = useState<User[]>(mockUsers);
  const [searchTerm, setSearchTerm] = useState("");
  const [showAddModal, setShowAddModal] = useState(false);
  const [editingUser, setEditingUser] = useState<User | null>(null);

  const filteredUsers = users.filter(
    (user) =>
      user.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      user.email.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const handleAddUser = (userData: Omit<User, "id">) => {
    const newUser: User = {
      ...userData,
      id: `user-${Date.now()}`,
    };
    setUsers([...users, newUser]);
    toast.success("User added successfully");
  };

  const handleEditUser = (userData: User) => {
    setUsers(users.map((user) => (user.id === userData.id ? userData : user)));
    setEditingUser(null);
    toast.success("User updated successfully");
  };

  const handleDeleteUser = (userId: string) => {
    setUsers(users.filter((user) => user.id !== userId));
    toast.success("User deleted successfully");
  };

  const handleToggleStatus = (userId: string) => {
    setUsers(
      users.map((user) =>
        user.id === userId
          ? {
              ...user,
              status: user.status === "Active" ? "Inactive" : "Active",
            }
          : user
      )
    );
    toast.success("User status updated successfully");
  };

  return (
    <div className="space-y-4 sm:space-y-6">
      {/* Header */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div className="relative flex-1 max-w-full sm:max-w-md">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
          <Input
            type="text"
            placeholder="Search users by name or email..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="pl-10 bg-slate-800 border-slate-700 text-white"
          />
        </div>

        <Button
          onClick={() => setShowAddModal(true)}
          className="bg-blue-500 hover:bg-blue-600 flex items-center justify-center space-x-2 w-full sm:w-auto text-white"
        >
          <Plus className="w-4 h-4" />
          <span>Add New User</span>
        </Button>
      </div>

      {/* Results count */}
      <div className="text-sm text-slate-400">
        {searchTerm && (
          <span>
            {filteredUsers.length} of {users.length} users found
          </span>
        )}
        {!searchTerm && <span>{users.length} total users</span>}
      </div>

      {/* User Table */}
      <UserTable
        users={filteredUsers}
        onEdit={setEditingUser}
        onDelete={handleDeleteUser}
        onToggleStatus={handleToggleStatus}
      />

      {/* Modals */}
      <AddUserModal
        isOpen={showAddModal}
        onClose={() => setShowAddModal(false)}
        onAdd={handleAddUser}
      />

      {editingUser && (
        <EditUserModal
          isOpen={!!editingUser}
          onClose={() => setEditingUser(null)}
          onEdit={handleEditUser}
          user={editingUser}
        />
      )}
    </div>
  );
}
