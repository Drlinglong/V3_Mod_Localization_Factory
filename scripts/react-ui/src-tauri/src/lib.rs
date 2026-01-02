#[cfg_attr(mobile, tauri::mobile_entry_point)]
use tauri_plugin_shell::ShellExt;

pub fn run() {
  tauri::Builder::default()
    .setup(|app| {
      if cfg!(debug_assertions) {
        app.handle().plugin(
          tauri_plugin_log::Builder::default()
            .level(log::LevelFilter::Info)
            .build(),
        )?;
      }
      app.handle().plugin(tauri_plugin_dialog::init())?;
      app.handle().plugin(tauri_plugin_shell::init())?;

      // Auto-start backend sidecar
      let sidecar_command = app.handle().shell().sidecar("web_server").map_err(|e| {
        eprintln!("Failed to create sidecar command: {}", e);
        e
      })?;
      
      let (mut _rx, _child) = sidecar_command.spawn().map_err(|e| {
         eprintln!("Failed to spawn sidecar: {}", e);
         e
      })?;

      Ok(())
    })
    .run(tauri::generate_context!())
    .expect("error while running tauri application");
}
