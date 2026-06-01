package com.gestordocumental.ui.documentos

import android.content.Intent
import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import androidx.fragment.app.Fragment
import androidx.lifecycle.lifecycleScope
import com.gestordocumental.data.RetrofitClient
import com.gestordocumental.data.SessionManager
import com.gestordocumental.databinding.FragmentDocumentosBinding
import kotlinx.coroutines.launch

class DocumentosFragment : Fragment() {

    private var _binding: FragmentDocumentosBinding? = null
    private val binding get() = _binding!!
    private lateinit var session: SessionManager
    private lateinit var adapter: DocumentosAdapter

    override fun onCreateView(inflater: LayoutInflater, container: ViewGroup?, savedInstanceState: Bundle?): View {
        _binding = FragmentDocumentosBinding.inflate(inflater, container, false)
        return binding.root
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        session = SessionManager(requireContext())

        adapter = DocumentosAdapter(
            onVerClick = { doc ->
                val intent = Intent(requireContext(), DocumentoDetalleActivity::class.java)
                intent.putExtra("doc_id", doc.idDocumento)
                startActivity(intent)
            },
            onEditClick = { doc ->
                val intent = Intent(requireContext(), DocumentoFormActivity::class.java)
                intent.putExtra("doc_id", doc.idDocumento)
                startActivity(intent)
            }
        )
        binding.rvDocumentos.adapter = adapter

        binding.fabNuevo.setOnClickListener {
            startActivity(Intent(requireContext(), DocumentoFormActivity::class.java))
        }

        binding.swipeRefresh.setOnRefreshListener { cargarDocumentos() }
        cargarDocumentos()
    }

    override fun onResume() {
        super.onResume()
        cargarDocumentos()
    }

    private fun cargarDocumentos(query: String? = null) {
        binding.swipeRefresh.isRefreshing = true
        lifecycleScope.launch {
            try {
                val resp = RetrofitClient.instance.getDocumentos(session.getToken(), query)
                if (resp.isSuccessful) {
                    adapter.submitList(resp.body()?.results ?: emptyList())
                    val empty = (resp.body()?.results?.isEmpty() == true)
                    binding.tvEmpty.visibility = if (empty) View.VISIBLE else View.GONE
                }
            } catch (e: Exception) {
                binding.tvEmpty.text = "Error de conexión"
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
