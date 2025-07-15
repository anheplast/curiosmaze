// src/router/index.js

import { createRouter, createWebHistory } from "vue-router";

// Vista de login y componentes
import Login from "../views/LoginView.vue"; // Vista de inicio de sesión
// Vista de Dashboard
import Dashboard from "@/views/Dashboard.vue";
// Vista de ejercicios
import PracticalExercises from "@/views/PracticalExercises.vue";

// Vista de acceso a evaluación
import LoginEvaluationView from "@/views/LoginEvaluationView.vue";
// Componente de evaluación
import CreateEvaluation from "@/components/docentes/crear-evaluacion/CreateEvaluation.vue"; // Crear evaluación
import ManageEvaluations from "@/components/docentes/gestion-evaluaciones/ManageEvaluations.vue"; // Gestionar evaluaciones
// Componente de gestión de estudiantes
import TeacherStudentManagement from "@/components/docentes/gestion-estudiantes/TeacherStudentManagement.vue"; // Gestión de estudiantes
// Vista de evaluación completada
import EvaluationCompleted from "@/views/EvaluationCompleted.vue"; // Evaluación completada

import StudentDashboard from "@/views/StudentDashboard.vue"; // Dashboard de estudiante


const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    // Ruta específica para login
    {
      path: "/login",
      name: "LoginView",
      component: Login,
      meta: { guestOnly: true },
    },
    {
      // Rutas de estudiante
      path: "/evaluation-access",
      name: "EvaluationAccess",
      component: LoginEvaluationView,
      meta: { requiresAuth: true, role: "estudiante" },
    },
    {
      path: "/estudiante/dashboard",
      name: "StudentDashboard",
      component: StudentDashboard,
      meta: { requiresAuth: true, role: "estudiante" },
    },
    {
      path: "/estudiante/historial-evaluaciones",
      name: "EvaluationHistory",
      component: () => import("../views/EvaluationHistoryView.vue"),
      meta: {
        requiresAuth: true,
        allowMultipleRoles: true, // Permitir múltiples roles
      },
    },
    // Mejorada: Ruta de resolución de ejercicios con props
    {
      path: "/resolucion-ejercicios-practicos",
      name: "PracticalExercises",
      component: PracticalExercises,
      meta: {
        requiresAuth: true,
        role: "estudiante",
        allowMultipleRoles: true, // Permitir acceso a docentes también
      },
      props: (route) => ({ evaluation_id: route.query.evaluation_id }),
    },
    // Ruta para ver resultados de evaluación
    {
      path: "/evaluacion-completada",
      name: "EvaluationCompleted",
      component: EvaluationCompleted,
      meta: { requiresAuth: true, role: "estudiante" },
      props: (route) => ({ evaluation_id: route.query.evaluation_id }),
    },
    // Rutas de docente
    {
      path: "/docente/dashboard",
      name: "DocenteDashboard",
      component: Dashboard,
      meta: { requiresAuth: true, role: "docente" },
      children: [
        {
          // Ruta por defecto - muestra la información general
          path: "",
          name: "DocenteHome",
          component: () => import("@/components/docentes/crear-evaluacion/CreateEvaluation.vue"),
        },
        {
          path: "crear-ejercicio",
          name: "CreateExercise",
          component: () => import("@/components/docentes/crear-ejercicio/CreateExercise.vue"),
        },
        // Nuevas rutas para evaluaciones
        {
          path: "crear-evaluacion",
          name: "CreateEvaluation",
          component: CreateEvaluation,
        },
        {
          path: "evaluaciones",
          name: "ManageEvaluations",
          component: ManageEvaluations,
        },
        {
          path: "editar-evaluacion/:id",
          name: "EditEvaluation",
          component: CreateEvaluation,
          props: true,
        },
        // Ruta para gestión de estudiantes
        {
          path: "estudiantes",
          name: "TeacherStudentManagement",
          component: TeacherStudentManagement,
        },
        {
          path: "repositorio-ejercicios",
          name: "TeacherExerciseRepository",
          component: () => import("@/components/docentes/repositorio-ejercicios/ExerciseRepository.vue"),
        },
      ],
    },
    // Rutas de admin
    {
      path: "/admin/dashboard",
      name: "AdminDashboard",
      component: Dashboard,
      meta: { requiresAuth: true, role: "admin" },
      children: [
        {
          // Ruta por defecto
          path: "",
          name: "AdminHome",
          component: () => import("@/components/admin/AdminHome.vue"),
        },
        {
          path: "crear-ejercicio",
          name: "AdminCreateExercise",
          component: () => import("@/components/docentes/crear-ejercicio/CreateExercise.vue"),
        },
        // Gestión de usuarios
        {
          path: "gestion-usuarios",
          name: "UserManagement",
          component: () => import("@/components/admin/gestion-usuarios/UserManagement.vue"),
        },
        {
          path: "repositorio-ejercicios",
          name: "AdminExerciseRepository",
          component: () => import("@/components/docentes/repositorio-ejercicios/ExerciseRepository.vue"),
        },
      ],
    },
    // Ruta de redirección para la ruta de dashboard
    {
      path: "/dashboard",
      redirect: (to) => {
        // Obtener el rol del usuario desde localStorage
        const userRole = localStorage.getItem("user_role");
        if (userRole === "docente") {
          return "/docente/dashboard";
        } else if (userRole === "admin") {
          return "/admin/dashboard";
        } else if (userRole === "estudiante") {
          return "/estudiante/dashboard"; // Redirige al dashboard de estudiante
        } else {
          return "/login"; // Redirigir al login si no hay rol definido
        }
      },
    },
    // Ruta para manejar 404
    {
      path: "/:pathMatch(.*)*",
      redirect: "/login", // Redirigir al login para páginas no encontradas
    },
  ],
});

// Navegación con protección por roles (mejorada para evitar redirecciones infinitas)
router.beforeEach((to, from, next) => {
  const requiresAuth = to.matched.some((record) => record.meta.requiresAuth);
  const guestOnly = to.matched.some((record) => record.meta.guestOnly);
  const token = localStorage.getItem("token");
  const userRole = localStorage.getItem("user_role");

  // Actualizar título de la página si está definido
  if (to.meta.title) {
    document.title = `${to.meta.title} | CURIOSMAZE`;
  } else {
    document.title = "CURIOSMAZE";
  }

  // Para rutas que requieren autenticación
  if (requiresAuth) {
    if (!token) {
      // Si se requiere autenticación pero no hay token, redirigir al login
      return next("/login");
    }

    // Si la ruta requiere un rol específico y NO permite múltiples roles
    if (to.meta.role && !to.meta.allowMultipleRoles && to.meta.role !== userRole) {
      // Redirige según el rol
      if (userRole === "docente") {
        return next("/docente/dashboard");
      } else if (userRole === "admin") {
        return next("/admin/dashboard");
      } else if (userRole === "estudiante") {
        return next("/evaluation-access");
      } else {
        // Si no tiene un rol válido, lo enviamos al login y limpiamos localStorage
        localStorage.removeItem("token");
        localStorage.removeItem("user_role");
        localStorage.removeItem("user_id");
        localStorage.removeItem("user_name");
        return next("/login");
      }
    }

    // Si todo está bien, permite el acceso
    return next();
  }

  // Para rutas solo de invitados (como el login)
  if (guestOnly && token) {
    // Si el usuario ya está autenticado, lo redirigimos según su rol
    if (userRole === "docente") {
      return next("/docente/dashboard");
    } else if (userRole === "admin") {
      return next("/admin/dashboard");
    } else if (userRole === "estudiante") {
      return next("/evaluation-access");
    } else {
      // Si no tiene un rol válido pero tiene token, limpiamos localStorage
      localStorage.removeItem("token");
      localStorage.removeItem("user_role");
      localStorage.removeItem("user_id");
      localStorage.removeItem("user_name");
    }
  }

  // En cualquier otro caso, permite la navegación
  next();
});

export default router;