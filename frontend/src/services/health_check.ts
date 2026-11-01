import axios from "axios";

import { axiosClient } from "./api";
import { API_BASE_URL } from "../config/api";


export async function isApiOK(): Promise<boolean> {
    const healthCheckUrl = new URL("/", API_BASE_URL).toString();

    try {
        const response = await axiosClient.get<{ status: string }>(healthCheckUrl);
        return response.data.status === "OK";
    } catch (error) {
        if (axios.isAxiosError(error)) {
            return false;
        }

        throw error;
    }
}