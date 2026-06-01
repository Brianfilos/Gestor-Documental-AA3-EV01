package com.gestordocumental.ui.dashboard

import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.TextView
import androidx.recyclerview.widget.RecyclerView
import com.gestordocumental.R
import com.gestordocumental.data.Documento

class DocumentoResumenAdapter(private val items: List<Documento>) :
    RecyclerView.Adapter<DocumentoResumenAdapter.VH>() {

    class VH(view: View) : RecyclerView.ViewHolder(view) {
        val tvTitulo: TextView = view.findViewById(R.id.tvDocTitulo)
        val tvClasificacion: TextView = view.findViewById(R.id.tvDocClasificacion)
        val tvEstado: TextView = view.findViewById(R.id.tvDocEstado)
        val tvFecha: TextView = view.findViewById(R.id.tvDocFecha)
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): VH {
        val v = LayoutInflater.from(parent.context).inflate(R.layout.item_documento_resumen, parent, false)
        return VH(v)
    }

    override fun onBindViewHolder(holder: VH, position: Int) {
        val doc = items[position]
        holder.tvTitulo.text = doc.titulo
        holder.tvClasificacion.text = doc.clasificacion_nombre
        holder.tvEstado.text = doc.estado.replaceFirstChar { it.uppercase() }
        holder.tvFecha.text = doc.fechaCarga
    }

    override fun getItemCount() = items.size
}
