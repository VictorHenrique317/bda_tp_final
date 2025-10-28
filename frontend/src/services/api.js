import axios from "axios";

const API_BASE_URL = "/api";

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000, // 30 seconds for file processing
});

export const chatAPI = {
  // Upload WhatsApp chat file
  uploadChat: async (file) => {
    const formData = new FormData();
    formData.append("file", file);

    const response = await api.post("/messages", formData, {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    });
    return response.data;
  },

  // Get list of all chats
  getChats: async () => {
    const response = await api.get("/messages/chats");
    return response.data;
  },

  // Get messages for a specific chat
  getMessages: async (chatId, limit = null) => {
    const params = limit ? { limit } : {};
    const response = await api.get(`/messages/${chatId}`, { params });
    return response.data;
  },

  // Get chat statistics
  getChatStats: async (chatId) => {
    const response = await api.get(`/messages/${chatId}/stats`);
    return response.data;
  },

  // Search for similar messages
  searchMessages: async (chatId, query, limit = 10) => {
    const response = await api.post("/embeddings/search", {
      chat_id: chatId,
      query: query,
      limit: limit,
    });
    return response.data;
  },

  // Get cluster coordinates for visualization
  getClusters: async (chatId) => {
    const response = await api.get(`/embeddings/${chatId}/clusters`);
    return response.data;
  },

  // Process chat to generate embeddings and clusters
  processChat: async (chatId) => {
    const response = await api.post(`/embeddings/${chatId}/process`);
    return response.data;
  },
};

export default api;

