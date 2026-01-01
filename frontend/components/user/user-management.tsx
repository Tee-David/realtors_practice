"use client";

import { useState, useEffect } from "react";
import { Plus, Search, RefreshCw } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { UserTable } from "./user-table";
import { AddUserModal } from "./add-user-modal";
import { EditUserModal } from "./edit-user-modal";
import type { User } from "@/lib/types";
import { toast } from "sonner";
import { useAuthAPI } from "@/hooks/useAuthAPI";

export function UserManagement() {
  const { listUsers, deleteUser: deleteUserAPI, loading } = useAuthAPI();
  const [users, setUsers] = useState<User[]>([]);
  const [searchTerm, setSearchTerm] = useState("");
  const [showAddModal, setShowAddModal] = useState(false);
  const [editingUser, setEditingUser] = useState<User | null>(null);
  const [isLoadingUsers, setIsLoadingUsers] = useState(true);

  // Fetch users from Firebase
  useEffect(() => {
    fetchUsers();
  }, []);

  const fetchUsers = async () => {
    setIsLoadingUsers(true);
    const result = await listUsers(1000); // Fetch up to 1000 users

    if (result.success && result.data?.users) {
      // Transform Firebase user data to match our User type
      const transformedUsers: User[] = result.data.users.map((fbUser: any) => ({
        id: fbUser.uid,
        name: fbUser.displayName || fbUser.email?.split('@')[0] || 'Unknown User',
        email: fbUser.email,
        role: fbUser.customClaims?.role || 'user',
        status: fbUser.disabled ? 'Inactive' : 'Active',
        lastLogin: fbUser.metadata?.lastSignInTime || 'Never',
        createdAt: fbUser.metadata?.creationTime || new Date().toISOString()
      }));
      setUsers(transformedUsers);
    } else {
      toast.error(result.error || 'Failed to fetch users');
    }
    setIsLoadingUsers(false);
  };

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

  const handleDeleteUser = async (userId: string) => {
    const result = await deleteUserAPI(userId);
    if (result.success) {
      setUsers(users.filter((user) => user.id !== userId));
      toast.success("User deleted successfully");
      // Refresh to get updated list from server
      await fetchUsers();
    } else {
      toast.error(result.error || "Failed to delete user");
    }
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

        <div className="flex gap-2 w-full sm:w-auto">
          <Button
            onClick={fetchUsers}
            disabled={isLoadingUsers}
            className="bg-slate-700 hover:bg-slate-600 flex items-center justify-center space-x-2 flex-1 sm:flex-initial text-white"
          >
            <RefreshCw className={`w-4 h-4 ${isLoadingUsers ? 'animate-spin' : ''}`} />
            <span>Refresh</span>
          </Button>
          <Button
            onClick={() => setShowAddModal(true)}
            className="bg-blue-500 hover:bg-blue-600 flex items-center justify-center space-x-2 flex-1 sm:flex-initial text-white"
          >
            <Plus className="w-4 h-4" />
            <span>Add User</span>
          </Button>
        </div>
      </div>

      {/* Results count */}
      <div className="text-sm text-slate-400">
        {isLoadingUsers ? (
          <span>Loading users from Firebase...</span>
        ) : (
          <>
            {searchTerm && (
              <span>
                {filteredUsers.length} of {users.length} users found
              </span>
            )}
            {!searchTerm && <span>{users.length} total users (from Firebase Auth)</span>}
          </>
        )}
      </div>

      {/* User Table */}
      {isLoadingUsers ? (
        <div className="flex items-center justify-center py-12">
          <RefreshCw className="w-8 h-8 animate-spin text-blue-500" />
        </div>
      ) : (
        <UserTable
          users={filteredUsers}
          onEdit={setEditingUser}
          onDelete={handleDeleteUser}
          onToggleStatus={handleToggleStatus}
        />
      )}

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
