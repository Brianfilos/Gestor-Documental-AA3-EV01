package com.gestordocumental.ui.historial

import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.TextView
import androidx.recyclerview.widget.RecyclerView
import com.gestordocumental.R
import com.gestordocumental.data.Historial

class HistorialAdapter(private val items: List<Historial>) :
    RecyclerView.Adapter<HistorialAdapter.VH>() {

    class VH(view: View) : RecyclerView.ViewHolder(view) {
        val tvAccion: TextView = view.findViewById(R.id.tvAccion)
        val tvDocumento: TextView = view.findViewById(R.id.tvDocumento)
        val tvUsuario: TextView = view.findViewById(R.id.tvUsuarioHist)
        val tvFecha: TextView = view.findViewById(R.id.tvFechaHist)
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): VH {
        val v = LayoutInflater.from(parent.context).inflate(R.layout.item_historial, parent, false)
        return VH(v)
    }

    override fun onBindViewHolder(holder: VH, position: Int) {
        val h = items[position]
        holder.tvAccion.text = h.accion
        holder.tvDocumento.text = h.documento_titulo
        holder.tvUsuario.text = h.usuario_nombre
        holder.tvFecha.text = h.fechaAccion
    }

    override fun getItemCount() = items.size
}
