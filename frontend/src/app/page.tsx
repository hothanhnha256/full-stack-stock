"use client";

import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { api, StockSymbol } from "@/lib/api";
import { Trash2, Plus, Send, Loader2 } from "lucide-react";

export default function Dashboard() {
  const [newCode, setNewCode] = useState("");
  const queryClient = useQueryClient();

  const { data: symbols = [], isLoading } = useQuery({
    queryKey: ["symbols"],
    queryFn: api.getSymbols,
  });

  const addMutation = useMutation({
    mutationFn: api.addSymbol,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["symbols"] });
      setNewCode("");
    },
  });

  const deleteMutation = useMutation({
    mutationFn: api.deleteSymbol,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["symbols"] }),
  });

  const sendMutation = useMutation({
    mutationFn: api.sendReport,
  });

  const handleAdd = (e: React.FormEvent) => {
    e.preventDefault();
    if (newCode.trim()) {
      addMutation.mutate(newCode.toUpperCase());
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900">
      <div className="container mx-auto px-4 py-12 max-w-6xl">
        {/* Header */}
        <div className="mb-12 text-center">
          <h1 className="text-5xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent mb-4">
            📊 Stock Report Manager
          </h1>
          <p className="text-gray-600 dark:text-gray-400 text-lg">
            Quản lý danh sách mã chứng khoán và gửi báo cáo tự động
          </p>
        </div>

        {/* Add Symbol Form */}
        <div className="mb-8 bg-white dark:bg-gray-800 rounded-2xl shadow-xl p-8 border border-gray-200 dark:border-gray-700">
          <form onSubmit={handleAdd} className="flex gap-4">
            <input
              type="text"
              value={newCode}
              onChange={(e) => setNewCode(e.target.value)}
              placeholder="Nhập mã (VD: VNM, FPT, DLG)"
              className="flex-1 px-6 py-4 border-2 border-gray-200 dark:border-gray-600 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white text-lg"
              disabled={addMutation.isPending}
            />
            <button
              type="submit"
              disabled={addMutation.isPending || !newCode.trim()}
              className="px-8 py-4 bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 text-white rounded-xl font-semibold flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-lg hover:shadow-xl text-lg"
            >
              {addMutation.isPending ? (
                <Loader2 className="w-5 h-5 animate-spin" />
              ) : (
                <Plus className="w-5 h-5" />
              )}
              Thêm mã
            </button>
          </form>
          {addMutation.isError && (
            <p className="text-red-500 mt-4 text-sm">
              ❌ {(addMutation.error as Error).message}
            </p>
          )}
        </div>

        {/* Symbols Table */}
        <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-xl overflow-hidden border border-gray-200 dark:border-gray-700 mb-8">
          <div className="px-8 py-6 border-b border-gray-200 dark:border-gray-700">
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
              Danh sách mã chứng khoán ({symbols.length})
            </h2>
          </div>

          {isLoading ? (
            <div className="flex justify-center items-center py-20">
              <Loader2 className="w-12 h-12 animate-spin text-blue-600" />
            </div>
          ) : symbols.length === 0 ? (
            <div className="text-center py-20 text-gray-500 dark:text-gray-400">
              <p className="text-xl">Chưa có mã nào. Hãy thêm mã đầu tiên!</p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-50 dark:bg-gray-700">
                  <tr>
                    <th className="px-8 py-4 text-left text-sm font-semibold text-gray-700 dark:text-gray-300">
                      #
                    </th>
                    <th className="px-8 py-4 text-left text-sm font-semibold text-gray-700 dark:text-gray-300">
                      Mã
                    </th>
                    <th className="px-8 py-4 text-left text-sm font-semibold text-gray-700 dark:text-gray-300">
                      Ngày thêm
                    </th>
                    <th className="px-8 py-4 text-right text-sm font-semibold text-gray-700 dark:text-gray-300">
                      Hành động
                    </th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
                  {symbols.map((symbol, index) => (
                    <tr
                      key={symbol.id}
                      className="hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors"
                    >
                      <td className="px-8 py-5 text-gray-900 dark:text-white font-medium">
                        {index + 1}
                      </td>
                      <td className="px-8 py-5">
                        <span className="px-4 py-2 bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200 rounded-lg font-bold text-lg">
                          {symbol.code}
                        </span>
                      </td>
                      <td className="px-8 py-5 text-gray-600 dark:text-gray-400">
                        {new Date(symbol.created_at).toLocaleString("vi-VN")}
                      </td>
                      <td className="px-8 py-5 text-right">
                        <button
                          onClick={() => {
                            if (confirm(`Xác nhận xóa ${symbol.code}?`)) {
                              deleteMutation.mutate(symbol.id);
                            }
                          }}
                          disabled={deleteMutation.isPending}
                          className="px-4 py-2 bg-red-100 hover:bg-red-200 dark:bg-red-900 dark:hover:bg-red-800 text-red-700 dark:text-red-200 rounded-lg font-semibold flex items-center gap-2 ml-auto transition-colors"
                        >
                          <Trash2 className="w-4 h-4" />
                          Xóa
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>

        {/* Send Report Button */}
        <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-xl p-8 border border-gray-200 dark:border-gray-700">
          <button
            onClick={() => sendMutation.mutate()}
            disabled={sendMutation.isPending || symbols.length === 0}
            className="w-full py-6 bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-700 hover:to-emerald-700 text-white rounded-xl font-bold text-xl flex items-center justify-center gap-3 disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-lg hover:shadow-xl"
          >
            {sendMutation.isPending ? (
              <>
                <Loader2 className="w-6 h-6 animate-spin" />
                Đang gửi báo cáo... (30-60 giây)
              </>
            ) : (
              <>
                <Send className="w-6 h-6" />
                📧 Gửi báo cáo ngay
              </>
            )}
          </button>
          {sendMutation.isSuccess && (
            <p className="text-green-600 dark:text-green-400 mt-4 text-center font-semibold">
              ✅ {sendMutation.data.message}
            </p>
          )}
          {sendMutation.isError && (
            <p className="text-red-500 mt-4 text-center">
              ❌ {(sendMutation.error as Error).message}
            </p>
          )}
          <p className="text-gray-500 dark:text-gray-400 mt-4 text-center text-sm">
            Báo cáo tự động: Mỗi ngày 4 giờ chiều (Thứ 2 - Thứ 6)
          </p>
        </div>
      </div>
    </div>
  );
}
