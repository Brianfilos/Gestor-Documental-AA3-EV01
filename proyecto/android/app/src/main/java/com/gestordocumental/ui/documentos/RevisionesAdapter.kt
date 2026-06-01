package com.gestordocumental.ui.documentos

import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.TextView
import androidx.recyclerview.widget.RecyclerView
import com.gestordocumental.R
import com.gestordocumental.data.Revision

class RevisionesAdapter(private val items: List<Revision>) :
    RecyclerView.Adapter<RevisionesAdapter.VH>() {

    class VH(view: View) : RecyclerView.ViewHolder(view) {
        val tvUsuario: TextView = view.findViewById(R.id.tvRevUsuario)
        val tvFecha: TextView = view.findViewById(R.id.tvRevFecha)
        val tvComentario: TextView = view.findViewById(R.id.tvRevComentario)
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): VH {
        val v = LayoutInflater.from(parent.context).inflate(R.layout.item_revision, parent, false)
        return VH(v)
    }

    override fun onBindViewHolder(holder: VH, position: Int) {
        val rev = items[position]
        holder.tvUsuario.text = rev.usuario_nombre
        holder.tvFecha.text = rev.fechaRevision
        holder.tvComentario.text = rev.comentario ?: ""
        holder.tvComentario.visibility = if (rev.comentario.isNullOrEmpty()) View.GONE else View.VISIBLE
    }

    override fun getItemCount() = items.size
}
