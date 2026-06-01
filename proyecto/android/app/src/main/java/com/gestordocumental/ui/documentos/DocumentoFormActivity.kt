package com.gestordocumental.ui.documentos

import android.os.Bundle
import android.view.View
import android.widget.ArrayAdapter
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.lifecycleScope
import com.gestordocumental.data.Clasificacion
import com.gestordocumental.data.Documento
import com.gestordocumental.data.RetrofitClient
import com.gestordocumental.data.SessionManager
import com.gestordocumental.databinding.ActivityDocumentoFormBinding
import kotlinx.coroutines.launch

class DocumentoFormActivity : AppCompatActivity() {

    private lateinit var binding: ActivityDocumentoFormBinding
    private lateinit var session: SessionManager
    private var docId: Int = 0
    private var clasificaciones: List<Clasificacion> = emptyList()
    private var docActual: Documento? = null

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityDocumentoFormBinding.inflate(layoutInflater)
        setContentView(binding.root)
        setSupportActionBar(binding.toolbar)
        supportActionBar?.setDisplayHomeAsUpEnabled(true)

        session = SessionManager(this)
        docId = intent.getIntExtra("doc_id", 0)
        supportActionBar?.title = if (docId == 0) "Nuevo Documento" else "Editar Documento"

        cargarClasificaciones()
        binding.btnGuardar.setOnClickListener { guardar() }
    }

    private fun cargarClasificaciones() {
        lifecycleScope.launch {
            try {
                val resp = RetrofitClient.instance.getClasificaciones(session.getToken())
                if (resp.isSuccessful) {
                    clasificaciones = resp.body()?.results ?: emptyList()
                    val nombres = clasificaciones.map { it.nombreClasificacion }
                    val adapter = ArrayAdapter(
                        this@DocumentoFormActivity,
                        android.R.layout.simple_dropdown_item_1line,
                        nombres
                    )
                    binding.autoClasificacion.setAdapter(adapter)

                    if (docId != 0) cargarDocumento()
                }
            } catch (e: Exception) {
                // silencioso
            }
        }
    }

    private fun cargarDocumento() {
        lifecycleScope.launch {
            try {
                val resp = RetrofitClient.instance.getDocumento(session.getToken(), docId)
                if (resp.isSuccessful) {
                    docActual = resp.body()
                    docActual?.let { doc ->
                        binding.etTitulo.setText(doc.titulo)
                        binding.etDescripcion.setText(doc.descripcion)
                        val clsNombre = clasificaciones.find { it.idClasificacion == doc.idClasificacion }?.nombreClasificacion
                        binding.autoClasificacion.setText(clsNombre, false)
                        val estadoIdx = listOf("activo","inactivo","revision","archivado").indexOf(doc.estado)
                        if (estadoIdx >= 0) binding.spinnerEstado.setSelection(estadoIdx)
                    }
                }
            } catch (e: Exception) {}
        }
    }

    private fun guardar() {
        val titulo = binding.etTitulo.text.toString().trim()
        val descripcion = binding.etDescripcion.text.toString().trim()
        val clsNombre = binding.autoClasificacion.text.toString()
        val clasificacion = clasificaciones.find { it.nombreClasificacion == clsNombre }

        if (titulo.isEmpty()) { binding.tilTitulo.error = "Ingresa el título"; return }
        if (clasificacion == null) { binding.tilClasificacion.error = "Selecciona una clasificación"; return }

        val estados = listOf("activo","inactivo","revision","archivado")
        val estado = estados[binding.spinnerEstado.selectedItemPosition]

        val doc = Documento(
            idDocumento = docId,
            titulo = titulo,
            descripcion = descripcion.ifEmpty { null },
            estado = estado,
            archivo = null,
            idClasificacion = clasificacion.idClasificacion
        )

        binding.btnGuardar.isEnabled = false
        lifecycleScope.launch {
            try {
                val token = session.getToken()
                val resp = if (docId == 0) {
                    RetrofitClient.instance.createDocumento(token, doc)
                } else {
                    RetrofitClient.instance.updateDocumento(token, docId, doc)
                }
                if (resp.isSuccessful) {
                    finish()
                } else {
                    binding.btnGuardar.isEnabled = true
                }
            } catch (e: Exception) {
                binding.btnGuardar.isEnabled = true
            }
        }
    }

    override fun onSupportNavigateUp(): Boolean {
        onBackPressedDispatcher.onBackPressed()
        return true
    }
}
