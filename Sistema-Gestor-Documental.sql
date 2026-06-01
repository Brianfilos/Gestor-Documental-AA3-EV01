SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='TRADITIONAL,ALLOW_INVALID_DATES';

-- -----------------------------------------------------
-- Schema sistema_gestor_documental
-- -----------------------------------------------------
CREATE SCHEMA IF NOT EXISTS `sistema_gestor_documental` DEFAULT CHARACTER SET utf8mb4;
USE `sistema_gestor_documental`;

-- -----------------------------------------------------
-- Table `clasificacion_documento`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `clasificacion_documento` (
  `idClasificacion` INT NOT NULL AUTO_INCREMENT,
  `nombreClasificacion` VARCHAR(100) NOT NULL,
  `descripcion` VARCHAR(255) NULL DEFAULT NULL,
  PRIMARY KEY (`idClasificacion`)
) ENGINE=InnoDB
DEFAULT CHARACTER SET = utf8mb4;

-- -----------------------------------------------------
-- Table `rol`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `rol` (
  `idRol` INT NOT NULL AUTO_INCREMENT,
  `nombreRol` VARCHAR(50) NOT NULL,
  PRIMARY KEY (`idRol`)
) ENGINE=InnoDB
DEFAULT CHARACTER SET = utf8mb4;

-- -----------------------------------------------------
-- Table `usuario`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `usuario` (
  `idUsuario` INT NOT NULL AUTO_INCREMENT,
  `nombre` VARCHAR(100) NOT NULL,
  `correo` VARCHAR(100) NOT NULL,
  `contrasena` VARCHAR(255) NOT NULL,
  `estado` VARCHAR(20) NOT NULL,
  `idRol` INT NULL DEFAULT NULL,
  PRIMARY KEY (`idUsuario`),
  UNIQUE INDEX `uq_usuario_correo` (`correo` ASC),
  INDEX `idx_usuario_idRol` (`idRol` ASC),
  CONSTRAINT `fk_usuario_rol`
    FOREIGN KEY (`idRol`)
    REFERENCES `rol` (`idRol`)
    ON DELETE SET NULL
    ON UPDATE CASCADE
) ENGINE=InnoDB
DEFAULT CHARACTER SET = utf8mb4;

-- -----------------------------------------------------
-- Table `documento`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `documento` (
  `idDocumento` INT NOT NULL AUTO_INCREMENT,
  `titulo` VARCHAR(200) NOT NULL,
  `descripcion` TEXT NULL DEFAULT NULL,
  `fechaCarga` DATE NOT NULL,
  `estado` VARCHAR(20) NOT NULL,
  `idUsuario` INT NOT NULL,
  `idClasificacion` INT NOT NULL,
  PRIMARY KEY (`idDocumento`),
  INDEX `idx_documento_idUsuario` (`idUsuario` ASC),
  INDEX `idx_documento_idClasificacion` (`idClasificacion` ASC),
  CONSTRAINT `fk_documento_usuario`
    FOREIGN KEY (`idUsuario`)
    REFERENCES `usuario` (`idUsuario`)
    ON DELETE RESTRICT
    ON UPDATE CASCADE,
  CONSTRAINT `fk_documento_clasificacion`
    FOREIGN KEY (`idClasificacion`)
    REFERENCES `clasificacion_documento` (`idClasificacion`)
    ON DELETE RESTRICT
    ON UPDATE CASCADE
) ENGINE=InnoDB
DEFAULT CHARACTER SET = utf8mb4;

-- -----------------------------------------------------
-- Table `historial_documento`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `historial_documento` (
  `idHistorial` INT NOT NULL AUTO_INCREMENT,
  `idDocumento` INT NOT NULL,
  `idUsuario` INT NOT NULL,
  `accion` VARCHAR(100) NOT NULL,
  `fechaAccion` DATETIME NOT NULL,
  PRIMARY KEY (`idHistorial`),
  INDEX `idx_historial_idDocumento` (`idDocumento` ASC),
  INDEX `idx_historial_idUsuario` (`idUsuario` ASC),
  CONSTRAINT `fk_historial_documento`
    FOREIGN KEY (`idDocumento`)
    REFERENCES `documento` (`idDocumento`)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  CONSTRAINT `fk_historial_usuario`
    FOREIGN KEY (`idUsuario`)
    REFERENCES `usuario` (`idUsuario`)
    ON DELETE RESTRICT
    ON UPDATE CASCADE
) ENGINE=InnoDB
DEFAULT CHARACTER SET = utf8mb4;

-- -----------------------------------------------------
-- Table `permiso`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `permiso` (
  `idPermiso` INT NOT NULL AUTO_INCREMENT,
  `nombrePermiso` VARCHAR(100) NOT NULL,
  PRIMARY KEY (`idPermiso`)
) ENGINE=InnoDB
DEFAULT CHARACTER SET = utf8mb4;

-- -----------------------------------------------------
-- Table `revision_documento`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `revision_documento` (
  `idRevision` INT NOT NULL AUTO_INCREMENT,
  `idDocumento` INT NOT NULL,
  `idUsuario` INT NOT NULL,
  `fechaRevision` DATE NOT NULL,
  `comentario` TEXT NULL DEFAULT NULL,
  PRIMARY KEY (`idRevision`),
  INDEX `idx_revision_idDocumento` (`idDocumento` ASC),
  INDEX `idx_revision_idUsuario` (`idUsuario` ASC),
  CONSTRAINT `fk_revision_documento`
    FOREIGN KEY (`idDocumento`)
    REFERENCES `documento` (`idDocumento`)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  CONSTRAINT `fk_revision_usuario`
    FOREIGN KEY (`idUsuario`)
    REFERENCES `usuario` (`idUsuario`)
    ON DELETE RESTRICT
    ON UPDATE CASCADE
) ENGINE=InnoDB
DEFAULT CHARACTER SET = utf8mb4;

-- -----------------------------------------------------
-- Table `rol_permiso`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `rol_permiso` (
  `idRol_Permiso` INT NOT NULL AUTO_INCREMENT,
  `idRol` INT NOT NULL,
  `idPermiso` INT NOT NULL,
  PRIMARY KEY (`idRol_Permiso`),
  INDEX `idx_rol_permiso_idRol` (`idRol` ASC),
  INDEX `idx_rol_permiso_idPermiso` (`idPermiso` ASC),
  CONSTRAINT `fk_rol_permiso_rol`
    FOREIGN KEY (`idRol`)
    REFERENCES `rol` (`idRol`)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  CONSTRAINT `fk_rol_permiso_permiso`
    FOREIGN KEY (`idPermiso`)
    REFERENCES `permiso` (`idPermiso`)
    ON DELETE CASCADE
    ON UPDATE CASCADE
) ENGINE=InnoDB
DEFAULT CHARACTER SET = utf8mb4;

SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;
