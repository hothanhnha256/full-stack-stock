import axios from "axios";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:5000";

export interface StockSymbol {
  id: number;
  code: string;
  created_at: string;
}

export const api = {
  async getSymbols(): Promise<StockSymbol[]> {
    const res = await axios.get(`${API_URL}/api/symbols`);
    return res.data;
  },

  async addSymbol(code: string): Promise<StockSymbol> {
    const res = await axios.post(`${API_URL}/api/symbols`, { code });
    return res.data;
  },

  async deleteSymbol(id: number): Promise<void> {
    await axios.delete(`${API_URL}/api/symbols/${id}`);
  },

  async sendReport(): Promise<{ message: string }> {
    const res = await axios.post(`${API_URL}/api/report/send`);
    return res.data;
  },
};
