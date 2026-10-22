Patch for the original Metro Exodus (M3) SDK for 4A Engine. 
Fixes the BC7 texture import error on modern GPU drivers by patching one line of the OpenCL kernel embedded in `uEditor_m.dll`.

### RU

Проявление:
При импорте текстур из `source/<папка>/*.png` редактор выдаёт сообщение: "Texture sources were changed. Reload Textures?:, а после «Да» падает с ошибкой: `#bc7::opencl_program_context::initialize: failed to build the program!`.

Причина:
BC7-энкодер в SDK работает на OpenCL. Его исходник (код от THQ) лежит открытым текстом внутри `uEditor_m.dll` и компилируется драйвером видеокарты при каждом запуске.
Современные драйверы (проверено на NVIDIA RTX 3050, Nvidia 596.49 Tue May 12, 2026) собирают его как OpenCL 2.x/3.0, где у указателей есть адресное пространство `__generic`. В коде есть строка, где указатель приводится к типу без указания адресного пространства: `bc7_quantize_endpoints(&quantized_endpoints, (float2x4 const*)&gd_subset_results[0], p_mode);`

Новый компилятор отвечает ошибкой: `error: passing 'const __generic float2x4 *' ... to parameter of type 'const float2x4 *' changes address space of pointer`
Старые драйверы собирали код как OpenCL 1.2, поэтому там проблемы не было (отсюда совет «откатить драйвер»).

Интересно, что `crnlib.cl` к этой ошибке не относится: он нужен crunch-компрессору (`crnlib.dll`), а не BC7. Оригинальный `crnlib.cl` собирается без ошибок, править его не нужно.

Что делает патч:
Заменяет в этой строке приведение на явное:c (float2x4 const*)	→	(float2x4 const __private*)

Новая строка длиннее на 10 байт, а менять размер данных в DLL нельзя. Поэтому скрипт убирает хвостовые пробелы и табы в строках исходника и добивает остаток пробелами до исходной длины. Код при этом не меняется.

Скрипт:
- находит исходник в DLL по сигнатуре, без жёстких смещений;
- проверяет, что нужная строка встречается ровно один раз;
- создаёт резервную копию `uEditor_m.dll.bak` (существующую не перезаписывает);
- умеет откатывать изменения и не применяется повторно.

Использование:
Нужен Python 3, сторонние библиотеки не требуются.

1. Закрой редактор и все процессы SDK (`uengine_m.exe`, `uCoordinator.exe`, `uService.exe` и прочие).
2. Запусти от администратора: `python patch_bc7.py ...\bin_x64\uEditor_m.dll`
3. Запусти редактор и импортируй текстуры.

Откат: `python patch_bc7.py C:\m3sdk\bin_x64\uEditor_m.dll --restore`

Как нашёл причину:
1. Исходник вытащен из DLL (поиск `__kernel` и границ строки по нулевым байтам).
2. Скомпилирован отдельно через `pyopencl`, откуда получился нормальный build log с номером строки.
3. Проверено, что с `-cl-std=CL1.2` код собирается без ошибок, значит дело в адресных пространствах OpenCL 2.0+.

Ограничения:
- Проверено на M3 SDK и RTX 3050.
- Если после патча ошибка осталась, значит она в другом месте kernel. Приложи build log (шаги выше) в Issue.
- Модифицированная `uEditor_m.dll` в репозиторий не включена, только скрипт.

Лицензия:
Использование, изменение и публикация разрешены при обязательном указании автора (VesTank) и ссылке на оригинальный репозиторий. Полный текст в файле LICENSE. Исходные файлы 4A Games / THQ не распространяются.

### UA

Прояв:
Під час імпорту текстур із `source/<тека>/*.png` редактор показує повідомлення "Texture sources were changed. Reload Textures?", а після «Так» падає з помилкою: `#bc7::opencl_program_context::initialize: failed to build the program!`.

Причина:
BC7-енкодер в SDK працює на OpenCL. Його вихідний код (код від THQ) лежить відкритим текстом усередині `uEditor_m.dll` і компілюється драйвером відеокарти при кожному запуску.
Сучасні драйвери (перевірено на NVIDIA RTX 3050, Nvidia 596.49 Tue May 12, 2026) збирають його як OpenCL 2.x/3.0, де в покажчиків є адресний простір `__generic`. У коді є рядок, де покажчик приводиться до типу без зазначення адресного простору:
`bc7_quantize_endpoints(&quantized_endpoints, (float2x4 const*)&gd_subset_results[0], p_mode);`

Новий компілятор відповідає помилкою: `error: passing 'const __generic float2x4 *' ... to parameter of type 'const float2x4 *' changes address space of pointer`
Старі драйвери збирали код як OpenCL 1.2, тому там проблеми не було (звідси порада «відкотити драйвер»).

Цікаво, що `crnlib.cl` до цієї помилки не причетний: він потрібен crunch-компресору (`crnlib.dll`), а не BC7. Оригінальний `crnlib.cl` збирається без помилок, правити його не потрібно.

Що робить патч:
Замінює в цьому рядку приведення на явне: `(float2x4 const*)` → `(float2x4 const __private*)`

Новий рядок довший на 10 байт, а змінювати розмір даних у DLL не можна. Тому скрипт прибирає кінцеві пробіли й табуляції в рядках вихідного коду та добиває залишок пробілами до початкової довжини. Код при цьому не змінюється.

Скрипт:
- знаходить вихідний код у DLL за сигнатурою, без жорстких зсувів;
- перевіряє, що потрібний рядок трапляється рівно один раз;
- створює резервну копію `uEditor_m.dll.bak` (наявну не перезаписує);
- вміє відкочувати зміни й не застосовується повторно.

Використання:
Потрібен Python 3, сторонні бібліотеки не потрібні.

1. Закрий редактор і всі процеси SDK (`uengine_m.exe`, `uCoordinator.exe`, `uService.exe` та інші).
2. Запусти від адміністратора: `python patch_bc7.py ...\bin_x64\uEditor_m.dll`
3. Запусти редактор і імпортуй текстури.

Відкат: `python patch_bc7.py C:\m3sdk\bin_x64\uEditor_m.dll --restore`

Як знайшов причину:
1. Вихідний код витягнуто з DLL (пошук `__kernel` і меж рядка за нульовими байтами).
2. Скомпільовано окремо через `pyopencl`, звідки вийшов нормальний build log з номером рядка.
3. Перевірено, що з `-cl-std=CL1.2` код збирається без помилок, отже річ в адресних просторах OpenCL 2.0+.

Обмеження:
- Перевірено на M3 SDK і RTX 3050.
- Якщо після патча помилка лишилася, вона в іншому місці kernel. Додай build log (кроки вище) до Issue.
- Модифікована `uEditor_m.dll` до репозиторію не включена, лише скрипт.

Ліцензія:
Використання, зміна та публікація дозволені за умови обов'язкового зазначення автора (VesTank) і посилання на оригінальний репозиторій. Повний текст у файлі LICENSE. Вихідні файли 4A Games / THQ не поширюються.

### EN

Symptom:
When importing textures from `source/<folder>/*.png`, the editor shows "Texture sources were changed. Reload Textures?", and after clicking "Yes" it crashes with: `#bc7::opencl_program_context::initialize: failed to build the program!`.

Cause:
The BC7 encoder in the SDK runs on OpenCL. Its source (THQ code) is stored as plain text inside `uEditor_m.dll` and is compiled by the GPU driver on every launch.
Modern drivers (tested on NVIDIA RTX 3050, Nvidia 596.49 Tue May 12, 2026) build it as OpenCL 2.x/3.0, where pointers have the `__generic` address space. One line casts a pointer to a type without specifying the address space:
`bc7_quantize_endpoints(&quantized_endpoints, (float2x4 const*)&gd_subset_results[0], p_mode);`

The new compiler fails with: `error: passing 'const __generic float2x4 *' ... to parameter of type 'const float2x4 *' changes address space of pointer`
Old drivers built the code as OpenCL 1.2, so there was no problem (hence the "roll back the driver" advice).

Interestingly, `crnlib.cl` is unrelated to this error: it is used by the crunch compressor (`crnlib.dll`), not by BC7. The original `crnlib.cl` builds without errors and doesn't need changes.

What the patch does:
Replaces the cast in this line with an explicit one: `(float2x4 const*)` → `(float2x4 const __private*)`

The new line is 10 bytes longer, and the size of the data in the DLL can't change. So the script strips trailing spaces and tabs from the source lines and pads the remainder with spaces to the original length. The code itself stays the same.

The script:
- finds the source in the DLL by signature, without hardcoded offsets;
- checks that the target line occurs exactly once;
- creates a backup `uEditor_m.dll.bak` (never overwrites an existing one);
- can roll back the changes and won't apply twice.

Usage:
Requires Python 3, no third-party libraries.

1. Close the editor and all SDK processes (`uengine_m.exe`, `uCoordinator.exe`, `uService.exe`, etc.).
2. Run as administrator: `python patch_bc7.py ...\bin_x64\uEditor_m.dll`
3. Launch the editor and import textures.

Rollback: `python patch_bc7.py C:\m3sdk\bin_x64\uEditor_m.dll --restore`

How the cause was found:
1. Extracted the source from the DLL (searched for `__kernel` and found line boundaries by null bytes).
2. Compiled it separately via `pyopencl`, which gave a proper build log with a line number.
3. Verified that with `-cl-std=CL1.2` the code builds without errors, so the problem is OpenCL 2.0+ address spaces.

Limitations:
- Tested on M3 SDK and RTX 3050.
- If the error persists after patching, it's somewhere else in the kernel. Attach the build log (steps above) to an Issue.
- The modified `uEditor_m.dll` is not included in the repository, only the script.

License:
Use, modification and publication are allowed provided that the original author (VesTank) is credited with a link to the original repository. See LICENSE for the full text. Original 4A Games / THQ files are not distributed.
