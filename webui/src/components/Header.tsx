import { useEffect, useState } from 'react';
import StorageUtils from '../utils/storage';
import { useAppContext } from '../utils/app.context';
import { classNames } from '../utils/misc';
import daisyuiThemes from 'daisyui/src/theming/themes';
import { THEMES } from '../Config';
// import { useNavigate } from 'react-router';

export default function Header() {
  // const navigate = useNavigate();
  const [selectedTheme, setSelectedTheme] = useState(StorageUtils.getTheme());
  // const { setShowSettings } = useAppContext();

  const setTheme = (theme: string) => {
    StorageUtils.setTheme(theme);
    setSelectedTheme(theme);
  };

  useEffect(() => {
    document.body.setAttribute('data-theme', selectedTheme);
    document.body.setAttribute(
      'data-color-scheme',
      // @ts-expect-error daisyuiThemes complains about index type, but it should work
      daisyuiThemes[selectedTheme]?.['color-scheme'] ?? 'auto'
    );
  }, [selectedTheme]);

  const { isGenerating, viewingChat } = useAppContext();
  const isCurrConvGenerating = isGenerating(viewingChat?.conv.id ?? '');

  // const removeConversation = () => {
  //   if (isCurrConvGenerating || !viewingChat) return;
  //   const convId = viewingChat?.conv.id;
  //   if (window.confirm('Are you sure to delete this conversation?')) {
  //     StorageUtils.remove(convId);
  //     navigate('/');
  //   }
  // };

  const downloadConversation = async () => {
    if (isCurrConvGenerating || !viewingChat) return;
    
    const convId = viewingChat?.conv.id;
    const conversationJson = JSON.stringify(viewingChat, null, 2);
    const blob = new Blob([conversationJson], { type: 'application/json' });
  
    try {
      // Verificando se a API está disponível no navegador
      if ('showSaveFilePicker' in window) {
        // Usar a API File System Access para abrir uma janela de salvar
        const fileHandle = await (window as any).showSaveFilePicker({
          suggestedName: `conversation_${convId}.json`,
          types: [
            {
              description: 'JSON Files',
              accept: { 'application/json': ['.json'] }
            }
          ]
        });
  
        // Criação de um arquivo no local escolhido
        const writableStream = await fileHandle.createWritable();
        await writableStream.write(blob);
        await writableStream.close();
        
        console.log('Arquivo salvo com sucesso!');
      } else {
        console.error('A API showSaveFilePicker não é suportada neste navegador.');
      }
    } catch (error) {
      console.error('Erro ao salvar o arquivo:', error);
    }
  };
  

  return (
    <div className="flex flex-row items-center pt-6 pb-6 sticky top-0 z-10 bg-base-100">
      {/* open sidebar button */}
      {/* <label htmlFor="toggle-drawer" className="btn btn-ghost lg:hidden">
        <svg
          xmlns="http://www.w3.org/2000/svg"
          width="16"
          height="16"
          fill="currentColor"
          className="bi bi-list"
          viewBox="0 0 16 16"
        >
          <path
            fillRule="evenodd"
            d="M2.5 12a.5.5 0 0 1 .5-.5h10a.5.5 0 0 1 0 1H3a.5.5 0 0 1-.5-.5m0-4a.5.5 0 0 1 .5-.5h10a.5.5 0 0 1 0 1H3a.5.5 0 0 1-.5-.5m0-4a.5.5 0 0 1 .5-.5h10a.5.5 0 0 1 0 1H3a.5.5 0 0 1-.5-.5"
          />
        </svg>
      </label> */}

      <div className="grow text-2xl font-bold ml-2">dPacioli (junior)</div>

      {/* action buttons (top right) */}
      <div className="flex items-center">
        {viewingChat && (
          <div className="dropdown dropdown-end">
            {/* "..." button */}
            <button
              tabIndex={0}
              role="button"
              className="btn m-1"
              disabled={isCurrConvGenerating}
            >
              <svg
                xmlns="http://www.w3.org/2000/svg"
                width="16"
                height="16"
                fill="currentColor"
                className="bi bi-three-dots-vertical"
                viewBox="0 0 16 16"
              >
                <path d="M9.5 13a1.5 1.5 0 1 1-3 0 1.5 1.5 0 0 1 3 0m0-5a1.5 1.5 0 1 1-3 0 1.5 1.5 0 0 1 3 0m0-5a1.5 1.5 0 1 1-3 0 1.5 1.5 0 0 1 3 0" />
              </svg>
            </button>
            {/* dropdown menu */}
            <ul
              tabIndex={0}
              className="dropdown-content menu bg-base-100 rounded-box z-[1] w-52 p-2 shadow"
            >
              <li onClick={downloadConversation}>
                <a>Download</a>
              </li>
              {/* <li className="text-error" onClick={removeConversation}>
                <a>Delete</a>
              </li> */}
            </ul>
          </div>
        )}

      

        {/* theme controller is copied from https://daisyui.com/components/theme-controller/ */}
        <div className="tooltip tooltip-bottom" data-tip="Themes">
          <div className="dropdown dropdown-end dropdown-bottom">
            <div tabIndex={0} role="button" className="btn m-1">
              <svg
                xmlns="http://www.w3.org/2000/svg"
                width="16"
                height="16"
                fill="currentColor"
                className="bi bi-palette2"
                viewBox="0 0 16 16"
              >
                <path d="M0 .5A.5.5 0 0 1 .5 0h5a.5.5 0 0 1 .5.5v5.277l4.147-4.131a.5.5 0 0 1 .707 0l3.535 3.536a.5.5 0 0 1 0 .708L10.261 10H15.5a.5.5 0 0 1 .5.5v5a.5.5 0 0 1-.5.5H3a3 3 0 0 1-2.121-.879A3 3 0 0 1 0 13.044m6-.21 7.328-7.3-2.829-2.828L6 7.188zM4.5 13a1.5 1.5 0 1 0-3 0 1.5 1.5 0 0 0 3 0M15 15v-4H9.258l-4.015 4zM0 .5v12.495zm0 12.495V13z" />
              </svg>
            </div>
            <ul
              tabIndex={0}
              className="dropdown-content bg-base-300 rounded-box z-[1] w-52 p-2 shadow-2xl h-80 overflow-y-auto"
            >
              <li>
                <button
                  className={classNames({
                    'btn btn-sm btn-block btn-ghost justify-start': true,
                    'btn-active': selectedTheme === 'auto',
                  })}
                  onClick={() => setTheme('auto')}
                >
                  auto
                </button>
              </li>
              {THEMES.map((theme) => (
                <li key={theme}>
                  <input
                    type="radio"
                    name="theme-dropdown"
                    className="theme-controller btn btn-sm btn-block btn-ghost justify-start"
                    aria-label={theme}
                    value={theme}
                    checked={selectedTheme === theme}
                    onChange={(e) => e.target.checked && setTheme(theme)}
                  />
                </li>
              ))}
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}
