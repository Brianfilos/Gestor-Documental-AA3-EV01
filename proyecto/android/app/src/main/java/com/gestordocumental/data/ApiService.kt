package com.gestordocumental.data

import retrofit2.Response
import retrofit2.http.*

// ---- Modelos de datos ----

data class LoginRequest(val correo: String, val password: String)

data class LoginResponse(
    val access: String,
    val refresh: String,
    val usuario: UsuarioInfo
)

data class UsuarioInfo(
    val id: Int,
    val nombre: String,
    val correo: String,
    val rol: String?
)

data class Documento(
    val idDocumento: Int = 0,
    val titulo: String,
    val descripcion: String?,
    val fechaCarga: String = "",
    val estado: String,
    val archivo: String?,
    val idUsuario: Int = 0,
    val usuario_nombre: String = "",
    val idClasificacion: Int,
    val clasificacion_nombre: String = ""
)

data class Clasificacion(
    val idClasificacion: Int,
    val nombreClasificacion: String,
    val descripcion: String?
)

data class Usuario(
    val idUsuario: Int,
    val nombre: String,
    val correo: String,
    val estado: String,
    val idRol: Int?,
    val rol_nombre: String?
)

data class Historial(
    val idHistorial: Int,
    val idDocumento: Int,
    val documento_titulo: String,
    val idUsuario: Int,
    val usuario_nombre: String,
    val accion: String,
    val fechaAccion: String
)

data class Revision(
    val idRevision: Int = 0,
    val idDocumento: Int,
    val idUsuario: Int = 0,
    val usuario_nombre: String = "",
    val fechaRevision: String = "",
    val comentario: String?
)

data class PaginatedResponse<T>(
    val count: Int,
    val next: String?,
    val previous: String?,
    val results: List<T>
)

// ---- Interfaz API ----

interface ApiService {

    @POST("auth/login/")
    suspend fun login(@Body request: LoginRequest): Response<LoginResponse>

    // Documentos
    @GET("documentos/")
    suspend fun getDocumentos(
        @Header("Authorization") token: String,
        @Query("q") query: String? = null,
        @Query("estado") estado: String? = null,
        @Query("clasificacion") clasificacion: Int? = null,
        @Query("page") page: Int? = null
    ): Response<PaginatedResponse<Documento>>

    @GET("documentos/{id}/")
    suspend fun getDocumento(
        @Header("Authorization") token: String,
        @Path("id") id: Int
    ): Response<Documento>

    @POST("documentos/")
    suspend fun createDocumento(
        @Header("Authorization") token: String,
        @Body documento: Documento
    ): Response<Documento>

    @PUT("documentos/{id}/")
    suspend fun updateDocumento(
        @Header("Authorization") token: String,
        @Path("id") id: Int,
        @Body documento: Documento
    ): Response<Documento>

    @DELETE("documentos/{id}/")
    suspend fun deleteDocumento(
        @Header("Authorization") token: String,
        @Path("id") id: Int
    ): Response<Unit>

    @GET("documentos/{id}/historial/")
    suspend fun getHistorialDocumento(
        @Header("Authorization") token: String,
        @Path("id") id: Int
    ): Response<List<Historial>>

    @GET("documentos/{id}/revisiones/")
    suspend fun getRevisiones(
        @Header("Authorization") token: String,
        @Path("id") id: Int
    ): Response<List<Revision>>

    @POST("documentos/{id}/revisiones/")
    suspend fun addRevision(
        @Header("Authorization") token: String,
        @Path("id") id: Int,
        @Body revision: Map<String, String>
    ): Response<Revision>

    // Clasificaciones
    @GET("clasificaciones/")
    suspend fun getClasificaciones(
        @Header("Authorization") token: String
    ): Response<PaginatedResponse<Clasificacion>>

    // Usuarios
    @GET("usuarios/")
    suspend fun getUsuarios(
        @Header("Authorization") token: String
    ): Response<PaginatedResponse<Usuario>>

    @GET("usuarios/me/")
    suspend fun getMe(
        @Header("Authorization") token: String
    ): Response<Usuario>

    // Historial global
    @GET("historial/")
    suspend fun getHistorial(
        @Header("Authorization") token: String
    ): Response<PaginatedResponse<Historial>>
}
