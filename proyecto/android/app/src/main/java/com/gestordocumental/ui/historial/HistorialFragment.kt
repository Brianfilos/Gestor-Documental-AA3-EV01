package com.gestordocumental.ui.historial

import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import androidx.fragment.app.Fragment
import androidx.lifecycle.lifecycleScope
import com.gestordocumental.data.RetrofitClient
import com.gestordocumental.data.SessionManager
import com.gestordocumental.databinding.FragmentHistorialBinding
import kotlinx.coroutines.launch

class HistorialFragment : Fragment() {

    private var _binding: FragmentHistorialBinding? = null
    private val binding get() = _binding!!
    private lateinit var session: SessionManager

    override fun onCreateView(inflater: LayoutInflater, container: ViewGroup?, savedInstanceState: Bundle?): View {
        _binding = FragmentHistorialBinding.inflate(inflater, container, false)
        return binding.root
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        session = SessionManager(requireContext())
        cargarHistorial()
        binding.swipeRefresh.setOnRefreshListener { cargarHistorial() }
    }

    private fun cargarHistorial() {
        binding.swipeRefresh.isRefreshing = true
        lifecycleScope.launch {
            try {
                val resp = RetrofitClient.instance.getHistorial(session.getToken())
                if (resp.isSuccessful) {
                    val items = resp.body()?.results ?: emptyList()
                    binding.rvHistorial.adapter = HistorialAdapter(items)
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
