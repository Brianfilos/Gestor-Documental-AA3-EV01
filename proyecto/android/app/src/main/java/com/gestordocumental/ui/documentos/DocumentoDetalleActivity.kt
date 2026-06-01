package com.gestordocumental.ui.documentos

import android.os.Bundle
import android.view.View
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.lifecycleScope
import com.gestordocumental.data.RetrofitClient
import com.gestordocumental.data.SessionManager
import com.gestordocumental.databinding.ActivityDocumentoDetalleBinding
import com.gestordocumental.ui.historial.HistorialAdapter
import kotlinx.coroutines.launch

class DocumentoDetalleActivity : AppCompatActivity() {

    private lateinit var binding: ActivityDocumentoDetalleBinding
    private lateinit var session: SessionManager
    private var docId: Int = 0

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityDocumentoDetalleBinding.inflate(layoutInflater)
        setContentView(binding.root)
        setSupportActionBar(binding.toolbar)
        supportActionBar?.setDisplayHomeAsUpEnabled(true)
        supportActionBar?.title = "Detalle de Documento"

        session = SessionManager(this)
        docId = intent.getIntExtra("doc_id", 0)

        binding.btnAgregarRevision.setOnClickListener { agregarRevision() }
        cargarDocumento()
    }

    private fun cargarDocumento() {
        lifecycleScope.launch {
            try {
                val token = session.getToken()
                val docResp = RetrofitClient.instance.getDocumento(token, docId)
                if (docResp.isSuccessful) {
                    val doc = docResp.body()!!
                    binding.tvTitulo.text = doc.titulo
                    binding.tvDescripcion.text = doc.descripcion ?: "Sin descripción"
                    binding.tvEstado.text = doc.estado.replaceFirstChar { it.uppercase() }
                    binding.tvClasificacion.text = doc.clasificacion_nombre
                    binding.tvFecha.text = doc.fechaCarga
                    binding.tvUsuario.text = doc.usuario_nombre
                }

                val histResp = RetrofitClient.instance.getHistorialDocumento(token, docId)
                if (histResp.isSuccessful) {
                    val items = histResp.body() ?: emptyList()
                    binding.rvHistorial.adapter = HistorialAdapter(items)
                }

                val revResp = RetrofitClient.instance.getRevisiones(token, docId)
                if (revResp.isSuccessful) {
                    val items = revResp.body() ?: emptyList()
                    binding.rvRevisiones.adapter = RevisionesAdapter(items)
                    binding.tvSinRevisiones.visibility =
                        if (items.isEmpty()) View.VISIBLE else View.GONE
                }
            } catch (e: Exception) {
                binding.tvTitulo.text = "Error al cargar"
            }
        }
    }

    private fun agregarRevision() {
        val comentario = binding.etComentario.text.toString().trim()
        if (comentario.isEmpty()) {
            binding.etComentario.error = "Escribe un comentario"
            return
        }
        lifecycleScope.launch {
            try {
                val resp = RetrofitClient.instance.addRevision(
                    session.getToken(), docId, mapOf("comentario" to comentario)
                )
                if (resp.isSuccessful) {
                    binding.etComentario.text?.clear()
                    cargarDocumento()
                }
            } catch (e: Exception) {
                // error silencioso
            }
        }
    }

    override fun onSupportNavigateUp(): Boolean {
        onBackPressedDispatcher.onBackPressed()
        return true
    }
}
