package com.gestordocumental.ui.usuarios

import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.TextView
import androidx.fragment.app.Fragment
import androidx.lifecycle.lifecycleScope
import androidx.recyclerview.widget.RecyclerView
import com.gestordocumental.R
import com.gestordocumental.data.RetrofitClient
import com.gestordocumental.data.SessionManager
import com.gestordocumental.data.Usuario
import com.gestordocumental.databinding.FragmentUsuariosBinding
import kotlinx.coroutines.launch

class UsuariosFragment : Fragment() {

    private var _binding: FragmentUsuariosBinding? = null
    private val binding get() = _binding!!
    private lateinit var session: SessionManager

    override fun onCreateView(inflater: LayoutInflater, container: ViewGroup?, savedInstanceState: Bundle?): View {
        _binding = FragmentUsuariosBinding.inflate(inflater, container, false)
        return binding.root
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        session = SessionManager(requireContext())
        cargarUsuarios()
        binding.swipeRefresh.setOnRefreshListener { cargarUsuarios() }
    }

    private fun cargarUsuarios() {
        binding.swipeRefresh.isRefreshing = true
        lifecycleScope.launch {
            try {
                val resp = RetrofitClient.instance.getUsuarios(session.getToken())
                if (resp.isSuccessful) {
                    val items = resp.body()?.results ?: emptyList()
                    binding.rvUsuarios.adapter = UsuariosAdapter(items)
                    binding.tvEmpty.visibility = if (items.isEmpty()) View.VISIBLE else View.GONE
                }
            } catch (e: Exception) {
                binding.tvEmpty.visibility = View.VISIBLE
            } finally {
                binding.swipeRefresh.isRefreshing = false
            }
        }
    }

    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
    }
}

class UsuariosAdapter(private val items: List<Usuario>) :
    RecyclerView.Adapter<UsuariosAdapter.VH>() {

    class VH(view: View) : RecyclerView.ViewHolder(view) {
        val tvNombre: TextView = view.findViewById(R.id.tvNombreUsuario)
        val tvCorreo: TextView = view.findViewById(R.id.tvCorreoUsuario)
        val tvRol: TextView = view.findViewById(R.id.tvRolUsuario)
        val tvEstado: TextView = view.findViewById(R.id.tvEstadoUsuario)
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): VH {
        val v = LayoutInflater.from(parent.context).inflate(R.layout.item_usuario, parent, false)
        return VH(v)
    }

    override fun onBindViewHolder(holder: VH, position: Int) {
        val u = items[position]
        holder.tvNombre.text = u.nombre
        holder.tvCorreo.text = u.correo
        holder.tvRol.text = u.rol_nombre ?: "Sin rol"
        holder.tvEstado.text = u.estado.replaceFirstChar { it.uppercase() }
    }

    override fun getItemCount() = items.size
}
