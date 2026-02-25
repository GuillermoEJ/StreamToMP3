import os
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "hide"
import pygame
from downloader import Downloader
from pathlib import Path
import time
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import threading
from abc import ABC, abstractmethod
from typing import List, Callable, Optional
import io
import sys


# ============ CORE CLASSES ============

class MusicPlayer:
    """Maneja la reproducción de música con pygame"""
    
    def __init__(self):
        self.is_playing = False
        self.is_paused = False
        try:
            pygame.mixer.init()
        except pygame.error as e:
            raise Exception(f"Audio initialization failed: {e}")
    
    def load(self, file_path: str) -> bool:
        """Cargar archivo de música"""
        try:
            pygame.mixer.music.load(file_path)
            return True
        except pygame.error as e:
            print(f"Error loading file: {e}")
            return False
    
    def play(self) -> bool:
        """Reproducir música"""
        try:
            pygame.mixer.music.play()
            self.is_playing = True
            self.is_paused = False
            return True
        except pygame.error as e:
            print(f"Error playing music: {e}")
            return False
    
    def pause(self) -> bool:
        """Pausar música"""
        try:
            pygame.mixer.music.pause()
            self.is_paused = True
            return True
        except pygame.error as e:
            print(f"Error pausing music: {e}")
            return False
    
    def resume(self) -> bool:
        """Reanudar música"""
        try:
            pygame.mixer.music.unpause()
            self.is_paused = False
            return True
        except pygame.error as e:
            print(f"Error resuming music: {e}")
            return False
    
    def stop(self) -> bool:
        """Detener música"""
        try:
            pygame.mixer.music.stop()
            self.is_playing = False
            self.is_paused = False
            return True
        except pygame.error as e:
            print(f"Error stopping music: {e}")
            return False
    
    def cleanup(self):
        """Limpiar recursos"""
        self.stop()
        pygame.mixer.quit()


class FileManager:
    """Maneja operaciones de archivos y carpetas"""
    
    @staticmethod
    def get_music_folders() -> List[str]:
        """Obtener carpetas en Music directory"""
        dir_path = str(Path.home() / "Music")
        try:
            folders = [name for name in os.listdir(dir_path)
                      if os.path.isdir(os.path.join(dir_path, name))]
            return sorted(folders)
        except Exception as e:
            print(f"Error getting folders: {e}")
            return []
    
    @staticmethod
    def get_music_files(folder_path: str) -> List[str]:
        """Obtener archivos .mp3 en una carpeta"""
        try:
            files = [f for f in os.listdir(folder_path)
                    if f.lower().endswith('.mp3')]
            return sorted(files)
        except Exception as e:
            print(f"Error getting music files: {e}")
            return []
    
    @staticmethod
    def get_full_path(folder: str, filename: str) -> str:
        """Obtener ruta completa de un archivo"""
        dir_path = str(Path.home() / "Music")
        return os.path.join(dir_path, folder, filename)
    
    @staticmethod
    def ensure_downloads_folder() -> str:
        """Asegurar que existe la carpeta de descargas"""
        music_folder = str(Path.home() / "Music")
        downloads = os.path.join(music_folder, "Downloads")
        if not os.path.exists(downloads):
            os.makedirs(downloads, exist_ok=True)
        return downloads


class MusicDownloader:
    """Maneja descargas de música desde diferentes fuentes"""
    
    def __init__(self):
        self.is_downloading = False
        self.downloads_folder = FileManager.ensure_downloads_folder()
    
    def download_spotify_playlist(self, url: str, callback: Optional[Callable] = None) -> bool:
        """Descargar playlist de Spotify"""
        self.is_downloading = True
        try:
            print(f"[*] Iniciando descarga de Spotify...")
            print(f"[*] URL: {url}")
            print(f"[*] Destino: {self.downloads_folder}")
            print(f"[*] Conectando con Spotify...")
            
            Downloader.download_spotify_playlist(url, self.downloads_folder)
            
            print(f"[+] ¡Descarga completada exitosamente!")
            if callback:
                callback(True, "Spotify playlist downloaded successfully!")
            return True
        except Exception as e:
            error_msg = f"Failed to download: {str(e)}"
            print(f"[-] Error: {error_msg}")
            if callback:
                callback(False, error_msg)
            return False
        finally:
            self.is_downloading = False
    
    def download_youtube(self, url: str, callback: Optional[Callable] = None) -> bool:
        """Descargar video de YouTube"""
        self.is_downloading = True
        try:
            print(f"[*] Iniciando descarga de YouTube...")
            print(f"[*] URL: {url}")
            print(f"[*] Destino: {self.downloads_folder}")
            print(f"[*] Procesando video...")
            
            Downloader.download_mp3(url, self.downloads_folder)
            
            print(f"[+] ¡Descarga completada exitosamente!")
            if callback:
                callback(True, "YouTube video downloaded successfully!")
            return True
        except Exception as e:
            error_msg = f"Failed to download: {str(e)}"
            print(f"[-] Error: {error_msg}")
            if callback:
                callback(False, error_msg)
            return False
        finally:
            self.is_downloading = False


# ============ UI CLASSES ============

class UITheme:
    """Configuración de tema para la interfaz"""
    
    BG_COLOR = '#000000'
    FG_COLOR = '#00ff00'
    ACCENT_COLOR = '#00ff88'
    BUTTON_BG = '#001a00'
    
    FONT_TITLE = ('Courier New', 16, 'bold')
    FONT_NORMAL = ('Courier New', 11)
    FONT_SMALL = ('Courier New', 9)


class Screen(ABC):
    """Clase base para pantallas de la aplicación"""
    
    def __init__(self, root: tk.Tk, on_back: Optional[Callable] = None):
        self.root = root
        self.on_back = on_back
        self.theme = UITheme()
    
    @abstractmethod
    def render(self):
        """Renderizar la pantalla"""
        pass
    
    def clear(self):
        """Limpiar todos los widgets"""
        for widget in self.root.winfo_children():
            widget.destroy()
    
    def create_button(self, parent, text: str, command: Callable, **kwargs):
        """Crear botón con estilo hacker"""
        default_kwargs = {
            'bg': self.theme.BUTTON_BG,
            'fg': self.theme.FG_COLOR,
            'activebackground': self.theme.FG_COLOR,
            'activeforeground': self.theme.BG_COLOR,
            'font': self.theme.FONT_NORMAL,
            'relief': 'raised',
            'bd': 2,
            'padx': 15,
            'pady': 8
        }
        default_kwargs.update(kwargs)
        return tk.Button(parent, text=text, command=command, **default_kwargs)


class SplashScreen(Screen):
    """Pantalla de inicio con título ASCII"""
    
    def __init__(self, root: tk.Tk, on_complete: Callable):
        super().__init__(root)
        self.on_complete = on_complete
    
    def render(self):
        """Mostrar pantalla de inicio"""
        self.clear()
        
        frame = tk.Frame(self.root, bg=self.theme.BG_COLOR)
        frame.pack(expand=True, fill='both')
        
        try:
            with open('title.txt', 'r') as file:
                title = file.read()
        except:
            title = "MP3 DOWNLOAD3R"
        
        label = tk.Label(frame, text=title, bg=self.theme.BG_COLOR,
                        fg=self.theme.FG_COLOR, font=('Courier New', 10),
                        justify='left')
        label.pack(expand=True)
        
        # Esperar 3 segundos
        self.root.after(3000, self.on_complete)


class MainMenuScreen(Screen):
    """Pantalla del menú principal"""
    
    def __init__(self, root: tk.Tk, on_playlist_select: Callable,
                 on_downloader: Callable, on_quit: Callable):
        super().__init__(root)
        self.on_playlist_select = on_playlist_select
        self.on_downloader = on_downloader
        self.on_quit = on_quit
        self.playlists = FileManager.get_music_folders()
    
    def render(self):
        """Renderizar menú principal"""
        self.clear()
        
        frame = tk.Frame(self.root, bg=self.theme.BG_COLOR)
        frame.pack(expand=True, fill='both', padx=20, pady=20)
        
        # Título
        title = tk.Label(frame, text=">> MP3 PLAYER <<",
                        bg=self.theme.BG_COLOR, fg=self.theme.FG_COLOR,
                        font=self.theme.FONT_TITLE)
        title.pack(pady=20)
        
        # Frame de playlists
        playlist_frame = tk.Frame(frame, bg=self.theme.BG_COLOR)
        playlist_frame.pack(fill='both', expand=True, pady=10)
        
        playlist_label = tk.Label(playlist_frame, text="[ PLAYLISTS ]",
                                 bg=self.theme.BG_COLOR, fg=self.theme.FG_COLOR,
                                 font=self.theme.FONT_NORMAL)
        playlist_label.pack()
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(playlist_frame)
        scrollbar.pack(side='right', fill='y')
        
        # Listbox
        self.playlist_listbox = tk.Listbox(playlist_frame,
                                           bg=self.theme.BG_COLOR,
                                           fg=self.theme.FG_COLOR,
                                           font=self.theme.FONT_NORMAL,
                                           yscrollcommand=scrollbar.set,
                                           height=10)
        self.playlist_listbox.pack(fill='both', expand=True)
        scrollbar.config(command=self.playlist_listbox.yview)
        
        for i, folder in enumerate(self.playlists, 1):
            self.playlist_listbox.insert(tk.END, f"{i}. {folder}")
        
        self.playlist_listbox.bind('<Double-Button-1>', 
                                   lambda e: self._on_select())
        
        # Botones
        button_frame = tk.Frame(frame, bg=self.theme.BG_COLOR)
        button_frame.pack(pady=10)
        
        self.create_button(button_frame, "▶ PLAY",
                          self._on_select).pack(side='left', padx=5)
        self.create_button(button_frame, "⬇ DOWNLOADER",
                          self.on_downloader).pack(side='left', padx=5)
        self.create_button(button_frame, "✕ QUIT",
                          self.on_quit).pack(side='left', padx=5)
    
    def _on_select(self):
        """Seleccionar playlist"""
        selection = self.playlist_listbox.curselection()
        if selection:
            self.on_playlist_select(self.playlists[selection[0]])
        else:
            messagebox.showwarning("Error", "Select a playlist first!")


class SongsScreen(Screen):
    """Pantalla de lista de canciones"""
    
    def __init__(self, root: tk.Tk, folder: str, on_play: Callable,
                 on_back: Callable):
        super().__init__(root, on_back)
        self.folder = folder
        self.on_play = on_play
        self.songs = FileManager.get_music_files(
            str(Path.home() / "Music" / folder)
        )
    
    def render(self):
        """Renderizar lista de canciones"""
        self.clear()
        
        if not self.songs:
            messagebox.showinfo("Info", "No MP3 files found!")
            self.on_back()
            return
        
        frame = tk.Frame(self.root, bg=self.theme.BG_COLOR)
        frame.pack(expand=True, fill='both', padx=20, pady=20)
        
        # Título
        title = tk.Label(frame, text="[ SONG LIST ]",
                        bg=self.theme.BG_COLOR, fg=self.theme.FG_COLOR,
                        font=self.theme.FONT_TITLE)
        title.pack(pady=10)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(frame)
        scrollbar.pack(side='right', fill='y')
        
        # Listbox
        self.songs_listbox = tk.Listbox(frame,
                                        bg=self.theme.BG_COLOR,
                                        fg=self.theme.FG_COLOR,
                                        font=self.theme.FONT_NORMAL,
                                        yscrollcommand=scrollbar.set)
        self.songs_listbox.pack(fill='both', expand=True)
        scrollbar.config(command=self.songs_listbox.yview)
        
        for i, song in enumerate(self.songs, 1):
            self.songs_listbox.insert(tk.END, f"{i}. {song}")
        
        self.songs_listbox.bind('<Double-Button-1>', 
                                lambda e: self._on_play())
        
        # Botones
        button_frame = tk.Frame(frame, bg=self.theme.BG_COLOR)
        button_frame.pack(pady=10)
        
        self.create_button(button_frame, "▶ PLAY",
                          self._on_play).pack(side='left', padx=5)
        self.create_button(button_frame, "◀ BACK",
                          self.on_back).pack(side='left', padx=5)
    
    def _on_play(self):
        """Reproducir canción seleccionada"""
        selection = self.songs_listbox.curselection()
        if selection:
            self.on_play(self.folder, self.songs[selection[0]])
        else:
            messagebox.showwarning("Error", "Select a song first!")


class PlayerScreen(Screen):
    """Pantalla de control de reproducción"""
    
    def __init__(self, root: tk.Tk, song_name: str, on_pause: Callable,
                 on_resume: Callable, on_stop: Callable, on_back: Callable):
        super().__init__(root, on_back)
        self.song_name = song_name
        self.on_pause_click = on_pause
        self.on_resume_click = on_resume
        self.on_stop_click = on_stop
    
    def render(self):
        """Renderizar pantalla de reproducción"""
        self.clear()
        
        frame = tk.Frame(self.root, bg=self.theme.BG_COLOR)
        frame.pack(expand=True, fill='both', padx=20, pady=20)
        
        # Info de canción
        song_label = tk.Label(frame, text="▶ Now Playing:",
                             bg=self.theme.BG_COLOR,
                             fg=self.theme.FG_COLOR,
                             font=self.theme.FONT_NORMAL)
        song_label.pack(pady=10)
        
        song_name = tk.Label(frame, text=self.song_name,
                            bg=self.theme.BG_COLOR,
                            fg=self.theme.ACCENT_COLOR,
                            font=self.theme.FONT_SMALL,
                            wraplength=700)
        song_name.pack(pady=5)
        
        info_label = tk.Label(frame, text="[ CONTROLS ]",
                             bg=self.theme.BG_COLOR,
                             fg=self.theme.FG_COLOR,
                             font=self.theme.FONT_NORMAL)
        info_label.pack(pady=20)
        
        # Botones de control
        control_frame = tk.Frame(frame, bg=self.theme.BG_COLOR)
        control_frame.pack(pady=20)
        
        self.create_button(control_frame, "⏸ PAUSE",
                          self.on_pause_click).pack(side='left', padx=10)
        self.create_button(control_frame, "▶ RESUME",
                          self.on_resume_click).pack(side='left', padx=10)
        self.create_button(control_frame, "⏹ STOP",
                          self.on_stop_click).pack(side='left', padx=10)
        
        # Botón volver
        self.create_button(frame, "◀ BACK TO SONGS",
                          self.on_back).pack(pady=20)


class DownloaderScreen(Screen):
    """Pantalla de herramienta de descargas"""
    
    def __init__(self, root: tk.Tk, on_spotify: Callable,
                 on_youtube: Callable, on_back: Callable):
        super().__init__(root, on_back)
        self.on_spotify = on_spotify
        self.on_youtube = on_youtube
    
    def render(self):
        """Renderizar pantalla de descargas"""
        self.clear()
        
        frame = tk.Frame(self.root, bg=self.theme.BG_COLOR)
        frame.pack(expand=True, fill='both', padx=20, pady=20)
        
        title = tk.Label(frame, text="[ DOWNLOADER TOOL ]",
                        bg=self.theme.BG_COLOR,
                        fg=self.theme.FG_COLOR,
                        font=self.theme.FONT_TITLE)
        title.pack(pady=20)
        
        self.create_button(frame, "Spotify Playlist",
                          self.on_spotify).pack(pady=10, fill='x')
        self.create_button(frame, "YouTube Video",
                          self.on_youtube).pack(pady=10, fill='x')
        self.create_button(frame, "◀ BACK",
                          self.on_back).pack(pady=20, fill='x')


class DownloadProgressScreen(Screen):
    """Pantalla de progreso de descarga con CD animado y logs"""
    
    def __init__(self, root: tk.Tk, message: str):
        super().__init__(root)
        self.message = message
        self.animation_frames = ["◷", "◶", "◵", "◴"]
        self.animation_index = 0
        self.cd_frames = ["◎", "◬", "◎", "◭"]
        self.cd_index = 0
        self.logs: List[str] = []
        self.is_animating = True
    
    def render(self):
        """Mostrar pantalla de descarga"""
        self.clear()
        
        frame = tk.Frame(self.root, bg=self.theme.BG_COLOR)
        frame.pack(expand=True, fill='both', padx=20, pady=20)
        
        # Título
        title_label = tk.Label(frame, text=self.message,
                              bg=self.theme.BG_COLOR,
                              fg=self.theme.FG_COLOR,
                              font=self.theme.FONT_TITLE)
        title_label.pack(pady=10)
        
        # CD Giratorio animado
        self.cd_label = tk.Label(frame, text="◎",
                                bg=self.theme.BG_COLOR,
                                fg=self.theme.ACCENT_COLOR,
                                font=('Courier New', 40, 'bold'))
        self.cd_label.pack(pady=20)
        
        # Área de logs
        log_label = tk.Label(frame, text="[ LOGS ]",
                            bg=self.theme.BG_COLOR,
                            fg=self.theme.FG_COLOR,
                            font=self.theme.FONT_NORMAL)
        log_label.pack()
        
        # Scrollbar para logs
        scrollbar = ttk.Scrollbar(frame)
        scrollbar.pack(side='right', fill='y')
        
        # Text widget para mostrar logs
        self.log_text = tk.Text(frame,
                               bg='#001a00',
                               fg=self.theme.ACCENT_COLOR,
                               font=self.theme.FONT_SMALL,
                               height=8,
                               yscrollcommand=scrollbar.set)
        self.log_text.pack(fill='both', expand=True, pady=10)
        scrollbar.config(command=self.log_text.yview)
        self.log_text.config(state='disabled')  # Read-only
        
        # Iniciar animación
        self.animate_cd()
    
    def animate_cd(self):
        """Animar el CD giratorio"""
        if self.is_animating:
            self.cd_index = (self.cd_index + 1) % len(self.cd_frames)
            self.cd_label.config(text=self.cd_frames[self.cd_index])
            self.root.after(150, self.animate_cd)
    
    def add_log(self, message: str):
        """Agregar línea de log"""
        self.logs.append(message)
        # Usar after para actualizar desde el thread de descarga
        self.root.after(0, self.update_logs)
    
    def update_logs(self):
        """Actualizar widget de logs"""
        self.log_text.config(state='normal')
        self.log_text.delete('1.0', tk.END)
        
        # Mostrar últimas 100 líneas
        lines_to_show = self.logs[-100:]
        self.log_text.insert(tk.END, '\n'.join(lines_to_show))
        
        # Scroll al final
        self.log_text.see(tk.END)
        self.log_text.config(state='disabled')
    
    def stop_animation(self):
        """Detener la animación"""
        self.is_animating = False


# ============ MAIN APPLICATION ============

class HackerMP3Player:
    """Aplicación principal del reproductor MP3"""
    
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("MP3 DOWNLOAD3R")
        self.root.geometry("800x600")
        self.root.configure(bg='#000000')
        
        # Componentes principales
        self.music_player = MusicPlayer()
        self.file_manager = FileManager()
        self.downloader = MusicDownloader()
        
        # Variables de estado
        self.current_folder: Optional[str] = None
        self.current_song: Optional[str] = None
        
        # Pantalla actual
        self.current_screen: Optional[Screen] = None
        
        # Mostrar pantalla de inicio
        self.show_splash_screen()
    
    def show_splash_screen(self):
        """Mostrar pantalla de inicio"""
        self.current_screen = SplashScreen(self.root, self.show_main_menu)
        self.current_screen.render()
    
    def show_main_menu(self):
        """Mostrar menú principal"""
        self.current_screen = MainMenuScreen(
            self.root,
            self.on_playlist_select,
            self.show_downloader_menu,
            self.quit_app
        )
        self.current_screen.render()
    
    def on_playlist_select(self, folder: str):
        """Manejar selección de playlist"""
        self.current_folder = folder
        self.show_songs_menu()
    
    def show_songs_menu(self):
        """Mostrar menú de canciones"""
        self.current_screen = SongsScreen(
            self.root,
            self.current_folder,
            self.on_song_select,
            self.show_main_menu
        )
        self.current_screen.render()
    
    def on_song_select(self, folder: str, song: str):
        """Manejar selección de canción"""
        self.current_song = song
        file_path = FileManager.get_full_path(folder, song)
        
        if self.music_player.load(file_path) and self.music_player.play():
            self.show_player_screen()
        else:
            messagebox.showerror("Error", "Cannot play file!")
    
    def show_player_screen(self):
        """Mostrar pantalla de reproducción"""
        self.current_screen = PlayerScreen(
            self.root,
            self.current_song,
            self.on_pause,
            self.on_resume,
            self.on_stop,
            self.show_songs_menu
        )
        self.current_screen.render()
    
    def on_pause(self):
        """Pausar música"""
        self.music_player.pause()
    
    def on_resume(self):
        """Reanudar música"""
        self.music_player.resume()
    
    def on_stop(self):
        """Detener música"""
        self.music_player.stop()
        self.show_songs_menu()
    
    def show_downloader_menu(self):
        """Mostrar menú de descargas"""
        if self.music_player.is_playing:
            self.music_player.stop()
        
        self.current_screen = DownloaderScreen(
            self.root,
            self.download_spotify,
            self.download_youtube,
            self.show_main_menu
        )
        self.current_screen.render()
    
    def download_spotify(self):
        """Descargar playlist de Spotify"""
        url = simpledialog.askstring("Spotify Downloader",
                                      "Enter Spotify playlist URL:")
        if url:
            self._start_download(url, self.downloader.download_spotify_playlist)
    
    def download_youtube(self):
        """Descargar video de YouTube"""
        url = simpledialog.askstring("YouTube Downloader",
                                      "Enter YouTube URL or song name:")
        if url:
            self._start_download(url, self.downloader.download_youtube)
    
    def _start_download(self, url: str, download_func: Callable):
        """Iniciar descarga en thread separado"""
        download_screen = DownloadProgressScreen(
            self.root,
            "Downloading..."
        )
        download_screen.render()
        self.current_screen = download_screen
        
        # Agregar logs iniciales
        download_screen.add_log("[*] Iniciando descarga...")
        download_screen.add_log(f"[*] URL: {url}")
        
        def on_download_complete(success: bool, message: str):
            download_screen.stop_animation()
            time.sleep(0.5)  # Dar tiempo para que se muestren últimos logs
            if success:
                messagebox.showinfo("Success", message)
            else:
                messagebox.showerror("Error", message)
            self.show_downloader_menu()
        
        class LogCapture:
            """Capturador de salida para mostrar logs en tiempo real"""
            def __init__(self, original, screen):
                self.original = original
                self.screen = screen
            
            def write(self, text):
                if text.strip():
                    self.screen.add_log(text.strip())
                self.original.write(text)
            
            def flush(self):
                self.original.flush()
        
        def download_with_logs():
            old_stdout = sys.stdout
            old_stderr = sys.stderr
            
            try:
                # Redirigir stdout/stderr
                sys.stdout = LogCapture(old_stdout, download_screen)
                sys.stderr = LogCapture(old_stderr, download_screen)
                
                # Ejecutar descarga
                download_func(url, on_download_complete)
                
            except Exception as e:
                download_screen.add_log(f"[-] ERROR: {str(e)}")
                on_download_complete(False, str(e))
            finally:
                sys.stdout = old_stdout
                sys.stderr = old_stderr
        
        thread = threading.Thread(target=download_with_logs, daemon=True)
        thread.start()
    
    def quit_app(self):
        """Cerrar aplicación"""
        self.music_player.cleanup()
        self.root.quit()


# ============ ENTRY POINT ============

def main():
    root = tk.Tk()
    app = HackerMP3Player(root)
    root.mainloop()


if __name__ == "__main__":
    main()