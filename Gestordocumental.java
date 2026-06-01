import java.sql.*;
import java.time.LocalDateTime;

public class Gestordocumental {

    public static void main(String[] args) {
        System.out.println("=== INICIANDO GESTOR DOCUMENTAL ===");
        
        
        String url = "jdbc:mysql://localhost:3307/test?useSSL=false&allowPublicKeyRetrieval=true";
        String usuario = "root";
        String password = ""; 

        // 1. OPERACIÓN: INSERCIÓN (Guardar un usuario de prueba asociado al rol 2)
        System.out.println("\n[Ejecutando Inserción...]");
        insertarUsuario(url, usuario, password, "Maria", "Gomez", "maria@mail.com", "clave123", "3159876543", "Activo", 2);

        // 2. OPERACIÓN: CONSULTA (Mostrar los usuarios guardados en la tabla)
        System.out.println("\n[Ejecutando Consulta...]");
        consultarUsuarios(url, usuario, password);

        // 3. OPERACIÓN: ACTUALIZACIÓN (Modificar el teléfono del usuario creado)
        System.out.println("\n[Ejecutando Actualización...]");
        actualizarUsuario(url, usuario, password, "maria@mail.com", "3200000000");

        // Consulta para verificar cambios en la consola
        System.out.println("\n[Consultando cambios...]");
        consultarUsuarios(url, usuario, password);

        // 4. OPERACIÓN: ELIMINACIÓN (Borrar al usuario de prueba para limpiar la tabla)
        System.out.println("\n[Ejecutando Eliminación...]");
        eliminarUsuario(url, usuario, password, "maria@mail.com");
    }

    // --- FUNCIONALIDAD INSERCIÓN ---
    public static void insertarUsuario(String url, String usuario, String password, String nombre, String apellido, String correo, String contraseña, String telefono, String estado, int idRol) {
        String sql = "INSERT INTO usuarios (nombre, apellido, correo, contraseña, telefono, estado, fecha_registro, id_rol) VALUES (?, ?, ?, ?, ?, ?, ?, ?)";
        
        try (Connection conexion = DriverManager.getConnection(url, usuario, password);
             PreparedStatement stats = conexion.prepareStatement(sql)) {
            
            stats.setString(1, nombre);
            stats.setString(2, apellido);
            stats.setString(3, correo);
            stats.setString(4, contraseña);
            stats.setString(5, telefono);
            stats.setString(6, estado);
            stats.setTimestamp(7, Timestamp.valueOf(LocalDateTime.now()));
            stats.setInt(8, idRol);
            
            stats.executeUpdate();
            System.out.println("-> OK: Usuario " + nombre + " insertado con éxito.");
        } catch (SQLException e) {
            System.out.println("-> Error en Inserción: " + e.getMessage());
        }
    }

    // --- FUNCIONALIDAD CONSULTA ---
    public static void consultarUsuarios(String url, String usuario, String password) {
        String sql = "SELECT id_usuario, nombre, correo, id_rol FROM usuarios";
        
        try (Connection conexion = DriverManager.getConnection(url, usuario, password);
             Statement stats = conexion.createStatement();
             ResultSet resultado = stats.executeQuery(sql)) {
            
            while (resultado.next()) {
                System.out.println("   ID: " + resultado.getInt("id_usuario") +
                                   " | Nombre: " + resultado.getString("nombre") +
                                   " | Correo: " + resultado.getString("correo") +
                                   " | Rol ID: " + resultado.getInt("id_rol"));
            }
        } catch (SQLException e) {
            System.out.println("-> Error en Consulta: " + e.getMessage());
        }
    }

    // --- FUNCIONALIDAD ACTUALIZACIÓN ---
    public static void actualizarUsuario(String url, String usuario, String password, String correo, String nuevoTelefono) {
        String sql = "UPDATE usuarios SET telefono = ? WHERE correo = ?";
        
        try (Connection conexion = DriverManager.getConnection(url, usuario, password);
             PreparedStatement stats = conexion.prepareStatement(sql)) {
            
            stats.setString(1, nuevoTelefono);
            stats.setString(2, correo);
            
            stats.executeUpdate();
            System.out.println("-> OK: Teléfono de " + correo + " actualizado.");
        } catch (SQLException e) {
            System.out.println("-> Error en Actualización: " + e.getMessage());
        }
    }

    // --- FUNCIONALIDAD ELIMINACIÓN ---
    public static void eliminarUsuario(String url, String usuario, String password, String correo) {
        String sql = "DELETE FROM usuarios WHERE correo = ?";
        
        try (Connection conexion = DriverManager.getConnection(url, usuario, password);
             PreparedStatement stats = conexion.prepareStatement(sql)) {
            
            stats.setString(1, correo);
            
            stats.executeUpdate();
            System.out.println("-> OK: Usuario " + correo + " eliminado.");
        } catch (SQLException e) {
            System.out.println("-> Error en Eliminación: " + e.getMessage());
        }
    }
}