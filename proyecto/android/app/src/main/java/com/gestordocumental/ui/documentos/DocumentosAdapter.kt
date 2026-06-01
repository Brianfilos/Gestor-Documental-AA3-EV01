package com.gestordocumental.ui.documentos

import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.TextView
import androidx.recyclerview.widget.DiffUtil
import androidx.recyclerview.widget.ListAdapter
import androidx.recyclerview.widget.RecyclerView
import com.gestordocumental.R
import com.gestordocumental.data.Documento
import com.google.android.material.button.MaterialButton
import com.google.android.material.chip.Chip

class DocumentosAdapter(
    private val onVerClick: (Documento) -> Unit,
    private val onEditClick: (Documento) -> Unit
) : ListAdapter<Documento, DocumentosAdapter.VH>(DIFF) {

    companion object {
        private val DIFF = object : DiffUtil.ItemCallback<Documento>() {
            override fun areItemsTheSame(a: Documento, b: Documento) = a.idDocumento == b.idDocumento
            override fun areContentsTheSame(a: Documento, b: Documento) = a == b
        }
    }

    class VH(view: View) : RecyclerView.ViewHolder(view) {
        val tvTitulo: TextView = view.findViewById(R.id.tvTitulo)
        val tvDescripcion: TextView = view.findViewById(R.id.tvDescripcion)
        val chipEstado: Chip = view.findViewById(R.id.chipEstado)
        val chipClasificacion: Chip = view.findViewById(R.id.chipClasificacion)
        val tvFecha: TextView = view.findViewById(R.id.tvFecha)
        val tvUsuario: TextView = view.findViewById(R.id.tvUsuario)
        val btnVer: MaterialButton = view.findViewById(R.id.btnVer)
        val btnEditar: MaterialButton = view.findViewById(R.id.btnEditar)
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): VH {
        val v = LayoutInflater.from(parent.context).inflate(R.layout.item_documento, parent, false)
        return VH(v)
    }

    override fun onBindViewHolder(holder: VH, position: Int) {
        val doc = getItem(position)
        holder.tvTitulo.text = doc.titulo
        holder.tvDescripcion.text = doc.descripcion ?: ""
        holder.tvDescripcion.visibility = if (doc.descripcion.isNullOrEmpty()) View.GONE else View.VISIBLE
        holder.chipEstado.text = doc.estado.replaceFirstChar { it.uppercase() }
        holder.chipClasificacion.text = doc.clasificacion_nombre
        holder.tvFecha.text = doc.fechaCarga
        holder.tvUsuario.text = doc.usuario_nombre
        holder.btnVer.setOnClickListener { onVerClick(doc) }
        holder.btnEditar.setOnClickListener { onEditClick(doc) }
    }
}
