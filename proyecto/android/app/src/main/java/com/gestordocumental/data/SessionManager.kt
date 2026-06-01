package com.gestordocumental.data

import android.content.Context
import android.content.SharedPreferences

class SessionManager(context: Context) {
    private val prefs: SharedPreferences =
        context.getSharedPreferences("gestor_prefs", Context.MODE_PRIVATE)

    companion object {
        const val KEY_TOKEN = "access_token"
        const val KEY_REFRESH = "refresh_token"
        const val KEY_USER_ID = "user_id"
        const val KEY_USER_NAME = "user_name"
        const val KEY_USER_EMAIL = "user_email"
        const val KEY_USER_ROL = "user_rol"
    }

    fun saveSession(response: LoginResponse) {
        prefs.edit().apply {
            putString(KEY_TOKEN, response.access)
            putString(KEY_REFRESH, response.refresh)
            putInt(KEY_USER_ID, response.usuario.id)
            putString(KEY_USER_NAME, response.usuario.nombre)
            putString(KEY_USER_EMAIL, response.usuario.correo)
            putString(KEY_USER_ROL, response.usuario.rol ?: "")
            apply()
        }
    }

    fun getToken(): String = "Bearer ${prefs.getString(KEY_TOKEN, "") ?: ""}"
    fun getUserName(): String = prefs.getString(KEY_USER_NAME, "") ?: ""
    fun getUserEmail(): String = prefs.getString(KEY_USER_EMAIL, "") ?: ""
    fun getUserRol(): String = prefs.getString(KEY_USER_ROL, "") ?: ""
    fun isLoggedIn(): Boolean = prefs.getString(KEY_TOKEN, null) != null

    fun clearSession() {
        prefs.edit().clear().apply()
    }
}
