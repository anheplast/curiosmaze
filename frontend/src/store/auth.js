// src/store/auth.js
import axios from 'axios';

// Estado inicial
const state = {
  isAuthenticated: localStorage.getItem('token') ? true : false,
  user: null,
  userRole: localStorage.getItem('user_role') || null,
  userId: localStorage.getItem('user_id') || null,
  userName: localStorage.getItem('user_name') || null,
};

// Getters
const getters = {
  isAuthenticated: state => state.isAuthenticated,
  user: state => state.user,
  userRole: state => state.userRole,
  userId: state => state.userId,
  userName: state => state.userName,
};

// Acciones
const actions = {
  // Iniciar sesión
  login({ commit }, userData) {
    // Guarda los datos del usuario autenticado
    localStorage.setItem('token', userData.token);
    localStorage.setItem('user_role', userData.rol);
    localStorage.setItem('user_id', userData.user_id);
    localStorage.setItem('user_name', userData.nombres);
    
    commit('SET_AUTH', userData);
    return Promise.resolve();
  },
  
  // Cerrar sesión
  logout({ commit }) {
    // Elimina los datos del usuario del localStorage
    localStorage.removeItem('token');
    localStorage.removeItem('user_role');
    localStorage.removeItem('user_id');
    localStorage.removeItem('user_name');
    
    commit('CLEAR_AUTH');
    return Promise.resolve();
  },
  
  // Inicializar el estado de autenticación desde localStorage
  initAuth({ commit }) {
    const token = localStorage.getItem('token');
    if (!token) {
      commit('CLEAR_AUTH');
      return;
    }
    
    const userData = {
      token: token,
      rol: localStorage.getItem('user_role'),
      user_id: localStorage.getItem('user_id'),
      nombres: localStorage.getItem('user_name')
    };
    
    commit('SET_AUTH', userData);
  }
};

// Mutaciones
const mutations = {
  SET_AUTH(state, userData) {
    state.isAuthenticated = true;
    state.userRole = userData.rol;
    state.userId = userData.user_id;
    state.userName = userData.nombres;
  },
  
  CLEAR_AUTH(state) {
    state.isAuthenticated = false;
    state.user = null;
    state.userRole = null;
    state.userId = null;
    state.userName = null;
  }
};

export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations
};