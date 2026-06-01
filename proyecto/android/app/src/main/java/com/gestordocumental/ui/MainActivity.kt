package com.gestordocumental.ui

import android.content.Intent
import android.os.Bundle
import android.view.MenuItem
import androidx.appcompat.app.ActionBarDrawerToggle
import androidx.appcompat.app.AppCompatActivity
import androidx.core.view.GravityCompat
import androidx.fragment.app.Fragment
import com.gestordocumental.R
import com.gestordocumental.data.SessionManager
import com.gestordocumental.databinding.ActivityMainBinding
import com.gestordocumental.ui.documentos.DocumentosFragment
import com.gestordocumental.ui.historial.HistorialFragment
import com.gestordocumental.ui.dashboard.DashboardFragment
import com.gestordocumental.ui.usuarios.UsuariosFragment
import com.google.android.material.navigation.NavigationView

class MainActivity : AppCompatActivity(), NavigationView.OnNavigationItemSelectedListener {

    private lateinit var binding: ActivityMainBinding
    private lateinit var session: SessionManager

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityMainBinding.inflate(layoutInflater)
        setContentView(binding.root)

        session = SessionManager(this)

        setSupportActionBar(binding.toolbar)

        // Drawer toggle
        val toggle = ActionBarDrawerToggle(
            this, binding.drawerLayout, binding.toolbar,
            R.string.nav_open, R.string.nav_close
        )
        binding.drawerLayout.addDrawerListener(toggle)
        toggle.syncState()

        binding.navView.setNavigationItemSelectedListener(this)

        // Info de usuario en el header
        val header = binding.navView.getHeaderView(0)
        header.findViewById<android.widget.TextView>(R.id.tvNavNombre).text = session.getUserName()
        header.findViewById<android.widget.TextView>(R.id.tvNavCorreo).text = session.getUserEmail()
        header.findViewById<android.widget.TextView>(R.id.tvNavRol).text = session.getUserRol()

        // Fragment inicial
        if (savedInstanceState == null) {
            loadFragment(DashboardFragment())
            binding.navView.setCheckedItem(R.id.nav_dashboard)
            supportActionBar?.title = "Dashboard"
        }
    }

    override fun onNavigationItemSelected(item: MenuItem): Boolean {
        when (item.itemId) {
            R.id.nav_dashboard -> {
                loadFragment(DashboardFragment())
                supportActionBar?.title = "Dashboard"
            }
            R.id.nav_documentos -> {
                loadFragment(DocumentosFragment())
                supportActionBar?.title = "Documentos"
            }
            R.id.nav_historial -> {
                loadFragment(HistorialFragment())
                supportActionBar?.title = "Historial"
            }
            R.id.nav_usuarios -> {
                loadFragment(UsuariosFragment())
                supportActionBar?.title = "Usuarios"
            }
            R.id.nav_logout -> {
                session.clearSession()
                startActivity(Intent(this, LoginActivity::class.java))
                finish()
            }
        }
        binding.drawerLayout.closeDrawer(GravityCompat.START)
        return true
    }

    private fun loadFragment(fragment: Fragment) {
        supportFragmentManager.beginTransaction()
            .replace(R.id.fragmentContainer, fragment)
            .commit()
    }

    override fun onBackPressed() {
        if (binding.drawerLayout.isDrawerOpen(GravityCompat.START)) {
            binding.drawerLayout.closeDrawer(GravityCompat.START)
        } else {
            super.onBackPressed()
        }
    }
}
