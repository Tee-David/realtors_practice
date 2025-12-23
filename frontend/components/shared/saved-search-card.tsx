"use client";

import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Switch } from "@/components/ui/switch";
import { Bell, Edit, Trash2, Eye, MapPin, Home } from "lucide-react";

interface SavedSearchCardProps {
  search: {
    id: string;
    name: string;
    query?: any;
    result_count?: number;
    new_matches?: number;
    email_alerts?: boolean;
    created_at?: string;
    last_run?: string;
  };
  onView?: () => void;
  onCheckNew?: () => void;
  onNotify?: () => void;
  onEdit?: () => void;
  onDelete?: () => void;
  onToggleEmail?: (enabled: boolean) => void;
}

export function SavedSearchCard({
  search,
  onView,
  onCheckNew,
  onNotify,
  onEdit,
  onDelete,
  onToggleEmail,
}: SavedSearchCardProps) {
  const query = search.query || {};
  const hasQuery = Object.keys(query).some((key) => query[key] !== undefined);

  return (
    <Card className="bg-slate-800 border-slate-700 hover:border-slate-600 transition-all">
      <CardContent className="p-6">
        <div className="space-y-4">
          {/* Header */}
          <div className="flex items-start justify-between gap-3">
            <div className="flex-1 min-w-0">
              <h3 className="text-lg font-semibold text-white mb-2 truncate">
                {search.name}
              </h3>

              {/* Criteria Display */}
              {hasQuery && (
                <div className="flex flex-wrap gap-2 mb-3">
                  {query.location && (
                    <Badge
                      variant="outline"
                      className="bg-blue-500/10 text-blue-400 border-blue-500/20 text-xs"
                    >
                      <MapPin className="w-3 h-3 mr-1" />
                      {query.location}
                    </Badge>
                  )}
                  {query.property_type && (
                    <Badge
                      variant="outline"
                      className="bg-purple-500/10 text-purple-400 border-purple-500/20 text-xs"
                    >
                      <Home className="w-3 h-3 mr-1" />
                      {query.property_type}
                    </Badge>
                  )}
                  {query.min_price && (
                    <Badge
                      variant="outline"
                      className="bg-green-500/10 text-green-400 border-green-500/20 text-xs"
                    >
                      ₦{query.min_price.toLocaleString()}+
                    </Badge>
                  )}
                  {query.max_price && (
                    <Badge
                      variant="outline"
                      className="bg-green-500/10 text-green-400 border-green-500/20 text-xs"
                    >
                      up to ₦{query.max_price.toLocaleString()}
                    </Badge>
                  )}
                  {query.bedrooms && (
                    <Badge
                      variant="outline"
                      className="bg-orange-500/10 text-orange-400 border-orange-500/20 text-xs"
                    >
                      {query.bedrooms}+ beds
                    </Badge>
                  )}
                  {query.listing_type && (
                    <Badge
                      variant="outline"
                      className="bg-cyan-500/10 text-cyan-400 border-cyan-500/20 text-xs"
                    >
                      {query.listing_type}
                    </Badge>
                  )}
                </div>
              )}
            </div>

            {/* New Matches Badge */}
            {search.new_matches && search.new_matches > 0 && (
              <Badge className="bg-red-500 text-white flex-shrink-0 animate-pulse">
                {search.new_matches} new
              </Badge>
            )}
          </div>

          {/* Stats */}
          <div className="flex items-center gap-4 text-sm">
            <div className="text-slate-400">
              <span className="font-semibold text-white text-lg">
                {search.result_count || 0}
              </span>{" "}
              <span className="text-slate-500">matches</span>
            </div>
            {search.created_at && (
              <div className="text-xs text-slate-500">
                Created {new Date(search.created_at).toLocaleDateString()}
              </div>
            )}
            {search.last_run && (
              <div className="text-xs text-slate-500">
                Last checked {new Date(search.last_run).toLocaleDateString()}
              </div>
            )}
          </div>

          {/* Email Notifications Toggle */}
          <div className="flex items-center justify-between py-3 px-4 bg-slate-900/50 rounded-lg border border-slate-700/50">
            <div className="flex items-center gap-2">
              <Bell className="w-4 h-4 text-slate-400" />
              <span className="text-sm text-slate-300">Email Alerts</span>
            </div>
            <Switch
              checked={search.email_alerts || false}
              onCheckedChange={onToggleEmail}
            />
          </div>

          {/* Actions */}
          <div className="grid grid-cols-2 gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={onView}
              className="border-slate-600 hover:bg-slate-700 hover:border-blue-500/30"
            >
              <Eye className="w-4 h-4 mr-2" />
              View All
            </Button>
            {onCheckNew && (
              <Button
                variant="outline"
                size="sm"
                onClick={onCheckNew}
                className="border-slate-600 hover:bg-slate-700 hover:border-green-500/30"
              >
                <Bell className="w-4 h-4 mr-2" />
                Check New
              </Button>
            )}
          </div>

          {/* Secondary Actions */}
          <div className="flex items-center gap-2">
            {onNotify && (
              <Button
                variant="outline"
                size="sm"
                onClick={onNotify}
                className="flex-1 border-slate-600 hover:bg-slate-700 text-xs"
              >
                <Bell className="w-3 h-3 mr-1" />
                Send Email
              </Button>
            )}
            <Button
              variant="outline"
              size="sm"
              onClick={onEdit}
              className="border-slate-600 hover:bg-slate-700"
              title="Edit search"
            >
              <Edit className="w-4 h-4" />
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={onDelete}
              className="border-red-500/30 hover:bg-red-500/10 text-red-400 hover:text-red-300"
              title="Delete search"
            >
              <Trash2 className="w-4 h-4" />
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
