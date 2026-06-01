package com.gestordocumental.ui.dashboard

import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import androidx.fragment.app.Fragment
import androidx.lifecycle.lifecycleScope
import com.gestordocumental.data.RetrofitClient
import com.gestordocumental.data.SessionManager
import com.gestordocumental.databinding.FragmentDashboardBinding
import kotlinx.coroutines.launch

class DashboardFragment : Fragment() {

    private var _binding: FragmentDashboardBinding? = null
    private val binding get() = _binding!!
    private lateinit var session: SessionManager

    override fun onCreateView(inflater: LayoutInflater, container: ViewGroup?, savedInstanceState: Bundle?): View {
        _binding = FragmentDashboardBinding.inflate(inflater, container, false)
        return binding.root
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        session = SessionManager(requireContext())
        binding.tvBienvenida.text = "Bienvenido, ${session.getUserName()}"
        cargarEstadisticas()
    }

    private fun cargarEstadisticas() {
        lifecycleScope.launch {
            try {
                val token = session.getToken()
                val docsResp = RetrofitClient.instance.getDocumentos(token)
                if (docsResp.isSuccessful) {
                    val body = docsResp.body()
                    binding.tvTotalDocs.text = body?.count?.toString() ?: "0"
                    val activos = body?.results?.count { it.estado == "activo" } ?: 0
                    binding.tvDocsActivos.text = activos.toString()
                    // Mostrar recientes
                    val recientes = body?.results?.take(5) ?: emptyList()
                    val adapter = DocumentoResumenAdapter(recientes)
                    binding.rvRecientes.adapter = adapter
                }
                val usersResp = RetrofitClient.instance.getUsuarios(token)
                if (usersResp.isSuccessful) {
                    binding.tvTotalUsuarios.text = usersResp.body()?.count?.toString() ?: "0"
                }
            } catch (e: Exception) {
                binding.tvTotalDocs.text = "—"
                binding.tvDocsActivos.text = "—"
                binding.tvTotalUsuarios.text = "—"
            }
        }
    }

    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
    }
}
