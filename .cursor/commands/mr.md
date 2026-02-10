Haz un commit de todos los cambios y luego un push al remoto.

1. **Añadir cambios**: ejecuta `git add -A` (o `git add .`) para incluir todos los archivos modificados y nuevos.
2. **Commit**: ejecuta `git commit` con un mensaje. Si el usuario ha escrito algo después de `/mr`, usa eso como mensaje de commit; si no, usa un mensaje breve y descriptivo basado en los cambios (por ejemplo "Update" o un resumen de los archivos tocados).
3. **Push**: ejecuta `git push`.

Si no hay cambios que commitear, dilo y no hagas push. Si el push falla (por ejemplo por conflictos o porque no hay upstream), informa del error.

Ejecuta los comandos en la terminal del proyecto, uno tras otro, y muestra la salida.
