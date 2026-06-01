package com.gestordocumental.ui

import android.content.Intent
import android.os.Bundle
import android.view.View
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.lifecycleScope
import com.gestordocumental.data.LoginRequest
import com.gestordocumental.data.RetrofitClient
import com.gestordocumental.data.SessionManager
import com.gestordocumental.databinding.ActivityLoginBinding
import kotlinx.coroutines.launch

class LoginActivity : AppCompatActivity() {

    private lateinit var binding: ActivityLoginBinding
    private lateinit var session: SessionManager

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityLoginBinding.inflate(layoutInflater)
        setContentView(binding.root)

        session = SessionManager(this)

        // Si ya está logueado, ir al dashboard
        if (session.isLoggedIn()) {
            goToDashboard()
            return
        }

        binding.btnLogin.setOnClickListener { doLogin() }
    }

    private fun doLogin() {
        val correo = binding.etCorreo.text.toString().trim()
        val password = binding.etPassword.text.toString()

        if (correo.isEmpty()) {
            binding.tilCorreo.error = "Ingresa tu correo"
            return
        }
        if (password.isEmpty()) {
            binding.tilPassword.error = "Ingresa tu contraseña"
            return
        }

        binding.tilCorreo.error = null
        binding.tilPassword.error = null
        setLoading(true)

        lifecycleScope.launch {
            try {
                val response = RetrofitClient.instance.login(LoginRequest(correo, password))
                if (response.isSuccessful && response.body() != null) {
                    session.saveSession(response.body()!!)
                    goToDashboard()
                } else {
                    showError("Correo o contraseña incorrectos")
                }
            } catch (e: Exception) {
                showError("Error de conexión: ${e.message}")
            } finally {
                setLoading(false)
            }
        }
    }

    private fun setLoading(loading: Boolean) {
        binding.btnLogin.isEnabled = !loading
        binding.progressBar.visibility = if (loading) View.VISIBLE else View.GONE
        binding.btnLogin.text = if (loading) "" else "Iniciar Sesión"
    }

    private fun showError(msg: String) {
        binding.tvError.text = msg
        binding.tvError.visibility = View.VISIBLE
    }

    private fun goToDashboard() {
        startActivity(Intent(this, MainActivity::class.java))
        finish()
    }
}
