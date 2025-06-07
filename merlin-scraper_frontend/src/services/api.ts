import { ApiResponse, Task } from "../types";

const API_BASE_URL = "http://localhost:3000";

export const login = async (): Promise<ApiResponse<null>> => {
  try {
    const response = await fetch(`${API_BASE_URL}/login`, {
      method: "GET",
      credentials: "include",
    });
    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.message || "Login failed");
    }

    return data;
  } catch (error) {
    console.error("Login error:", error);
    throw error;
  }
};

export const generateTasks = async (
  limit: number
): Promise<ApiResponse<null>> => {
  try {
    const response = await fetch(
      `${API_BASE_URL}/generate_tasks?limit=${limit}`,
      {
        method: "GET",
        credentials: "include",
      }
    );

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.message || "Task generation failed");
    }

    return data;
  } catch (error) {
    console.error("Generate tasks error:", error);
    throw error;
  }
};

export const fetchTasks = async (): Promise<ApiResponse<Task>> => {
  try {
    const response = await fetch(`${API_BASE_URL}/tasks`, {
      method: "GET",
      credentials: "include",
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.message || "Failed to fetch tasks");
    }

    return data;
  } catch (error) {
    console.error("Fetch tasks error:", error);
    throw error;
  }
};

// ✅ Nova funkcija: Pokretanje DINP scrape + parsiranja
export const processDINP = async (): Promise<void> => {
  try {
    const response = await fetch(`${API_BASE_URL}/process_dinp`, {
      method: "GET",
      credentials: "include",
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.error || "Neuspješno procesiranje DINP-a");
    }

    console.log("DINP obrada gotova:", data.message);
  } catch (error) {
    console.error("Process DINP error:", error);
    throw error;
  }
};
