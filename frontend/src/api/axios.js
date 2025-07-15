// src/api/axios.js
import axios from "axios";
import store from '@/store';
import router from '@/router';

// Configuración base - TIMEOUT AUMENTADO para operaciones batch
const API_URL = import.meta.env.VITE_API_URL;
const DEFAULT_TIMEOUT = 60000; // 60 segundos

// Crear una instancia de axios con configuración base
const axiosInstance = axios.create({
  baseURL: API_URL,
  timeout: DEFAULT_TIMEOUT,
  headers: {
    "Content-Type": "application/json",
    "Accept": "application/json"
  },
  withCredentials: true,
});

// Configuración para CSRF
axiosInstance.defaults.xsrfCookieName = "csrftoken";
axiosInstance.defaults.xsrfHeaderName = "X-CSRFToken";

// Función para obtener cookies
function getCookie(name) {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) return parts.pop().split(";").shift();
}

// Interceptor para añadir token de autenticación y CSRF, y detectar batch
axiosInstance.interceptors.request.use(
  (config) => {
    // --- Autorización ---
    const token = localStorage.getItem("token");
    if (token) {
      config.headers["Authorization"] = token.startsWith("Bearer ")
        ? token
        : `Bearer ${token}`;
      console.log(
        `Enviando petición con token: ${config.headers["Authorization"].substring(0, 20)}...`
      );
    } else {
      console.log("ADVERTENCIA: No se encontró token en localStorage");
    }

    // --- CSRF para mutaciones ---
    if (["post", "put", "delete"].includes(config.method)) {
      const csrfToken = getCookie("csrftoken");
      if (csrfToken) {
        config.headers["X-CSRFToken"] = csrfToken;
        console.log(`Token CSRF incluido: ${csrfToken.substring(0, 10)}...`);
      } else {
        console.log("ADVERTENCIA: No se encontró token CSRF en cookies");
      }
    }

    // --- Detectar operaciones batch ---
    // Convertimos config.data a string para poder usar .includes de forma segura
    const dataString =
      typeof config.data === "string"
        ? config.data
        : JSON.stringify(config.data || {});

    if (config.url?.includes("batch") || dataString.includes("batch")) {
      console.log(
        `🔄 BATCH OPERATION: ${config.method?.toUpperCase()} ${config.url} - Timeout: ${config.timeout}ms`
      );
      if (config.timeout < DEFAULT_TIMEOUT) {
        console.log(
          `⚠️ Aumentando timeout para operación batch de ${config.timeout}ms a ${DEFAULT_TIMEOUT}ms`
        );
        config.timeout = DEFAULT_TIMEOUT;
      }
    } else {
      console.log(`Petición a: ${config.method?.toUpperCase()} ${config.url}`);
    }

    return config;
  },
  (error) => {
    console.error("Error en interceptor de solicitud:", error);
    return Promise.reject(error);
  }
);

// Interceptor para manejar respuestas y errores
axiosInstance.interceptors.response.use(
  (response) => {
    console.log(
      `Respuesta recibida de ${response.config.url} con estado ${response.status}`
    );
    return response;
  },
  (error) => {
    console.error("Error en respuesta:", error);

    if (error.response) {
      console.error(
        `Estado HTTP: ${error.response.status} ${error.response.statusText}`
      );
      console.error("Datos de respuesta:", error.response.data);
      console.error("Encabezados:", error.response.headers);

      // Error CSRF
      if (
        error.response.status === 403 &&
        typeof error.response.data === "string" &&
        error.response.data.includes("CSRF")
      ) {
        console.error("Error CSRF detectado. Intentando renovar token...");
        // Lógica opcional para refrescar CSRF
      }

      // Sesión expirada (401) - Manejo mejorado con Vuex y Router
      if (
        error.response.status === 401 &&
        !error.config.url.includes("login") &&
        !error.config.url.includes("register")
      ) {
        console.error("Sesión expirada o token inválido. Redirigiendo al login...");
        
        // Limpiar datos de autenticación de localStorage
        localStorage.removeItem('token');
        localStorage.removeItem('user_role');
        localStorage.removeItem('user_id');
        localStorage.removeItem('user_name');
        
        // Cerrar sesión en Vuex store
        store.dispatch('auth/logout');
        
        // Redirigir al login si no estamos ya ahí
        if (router.currentRoute.value.path !== '/') {
          router.push('/');
        }
      }
    } else if (error.request) {
      console.error("No se recibió respuesta del servidor:", error.request);

      // Más detalles para batch
      const cfg = error.config || {};
      const dataString =
        typeof cfg.data === "string"
          ? cfg.data
          : JSON.stringify(cfg.data || {});
      if (cfg.url?.includes("batch") || dataString.includes("batch")) {
        console.error("⚠️ ERROR EN OPERACIÓN BATCH:");
        console.error(`URL: ${cfg.url}`);
        console.error(`Método: ${cfg.method}`);
        console.error(`Timeout: ${cfg.timeout}ms`);
        if (error.code === "ECONNABORTED") {
          console.error("⏱️ TIMEOUT EXCEDIDO en operación batch.");
        }
      }
    } else {
      console.error("Error en configuración de la petición:", error.message);
    }

    return Promise.reject(error);
  }
);

export default axiosInstance;