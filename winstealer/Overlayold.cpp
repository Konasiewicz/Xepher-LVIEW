#include "Overlay.h"
#include "Utils.h"
#include "Structs.h"
#include "LeagueMemoryReader.h"
#include "Benchmark.h"

#include <string>
#include <list>

#define HCheck(x, m) if(x != S_OK) { throw std::runtime_error(Character::Format("DirectX: Failed at %s. Error code: %d\n", m, MAKE_HRESULT(1, _FACDXGI, X))); }

ID3D11Device*            Overlay::dxDevice            = NULL;
ID3D11DeviceContext*     Overlay::dxDeviceContext     = NULL;
IDXGISwapChain1*         Overlay::dxSwapChain            = NULL;
ID3D11RenderTargetView*  Overlay::dxRenderTarget  = NULL;

Overlay::Overlay(): configs(*(ConfigSet::Get())){
}

constexpr auto windowFlags = ImGuiWindowFlags_NoCollapse | ImGuiWindowFlags_NoResize
| ImGuiWindowFlags_NoScrollbar | ImGuiWindowFlags_NoScrollWithMouse;

void Overlay::Init() {

	// Create transparent window
	std::string windowClassName = Character::RandomString(10);
	std::string windowName = Character::RandomString(10);
	SetConsoleTitleA(windowName.c_str());
	
	// Create window with random name & class name
	WNDCLASSEXA wc = { sizeof(WNDCLASSEX), CS_CLASSDC, WndProc, 0L, 0L, GetModuleHandle(NULL), NULL, NULL, NULL, NULL, windowClassName.c_str(), NULL };
	RegisterClassExA(&wc);
	hWindow = CreateWindowExA(
		WS_EX_TOPMOST | WS_EX_NOACTIVATE | WS_EX_LAYERED,
		windowClassName.c_str(), windowName.c_str(),
		WS_POPUP,
		1, 1, GetSystemMetrics(SM_CXSCREEN), GetSystemMetrics(SM_CYSCREEN),
		nullptr, nullptr, GetModuleHandle(0), nullptr);

	if (hWindow == NULL) {
		throw WinApiException("Failed to create overlay window");
	}
	
	ShowWindow(hWindow, SW_SHOW);

	// Initialize Direct3D
	if (!CreateDeviceD3D(hWindow))
	{
		CleanupDeviceD3D();
		throw std::runtime_error("Failed to create D3D device");
	}

	// Setup imgui context
	IMGUI_CHECKVERSION();
	ImGui::CreateContext();
	ImGuiIO& io = ImGui::GetIO(); (void)io;
	io.ConfigWindowsMoveFromTitleBarOnly = true;

	// Setup Dear ImGui style
	ImGui::StyleColorsLight();
	ImGuiStyle& style = ImGui::GetStyle();

	// Setup Platform/Renderer backends
	ImGui_ImplWin32_Init(hWindow);
	ImGui_ImplDX11_Init(dxDevice, dxDeviceContext);

	ImGui::GetStyle().FrameRounding = 4.0f;
	ImGui::GetStyle().GrabRounding = 4.0f;
	style.ScrollbarSize = 9.0f;

	ImVec4* colors = ImGui::GetStyle().Colors;
	colors[ImGuiCol_Text] = ImVec4(0.95f, 0.96f, 0.98f, 1.00f);
	colors[ImGuiCol_TextDisabled] = ImVec4(0.36f, 0.42f, 0.47f, 1.00f);
	colors[ImGuiCol_WindowBg] = ImVec4(0.11f, 0.15f, 0.17f, 1.00f);
	colors[ImGuiCol_ChildBg] = ImVec4(0.15f, 0.18f, 0.22f, 1.00f);
	colors[ImGuiCol_PopupBg] = ImVec4(0.08f, 0.08f, 0.08f, 0.94f);
	colors[ImGuiCol_Border] = ImVec4(0.08f, 0.10f, 0.12f, 1.00f);
	colors[ImGuiCol_BorderShadow] = ImVec4(0.00f, 0.00f, 0.00f, 0.00f);
	colors[ImGuiCol_FrameBg] = ImVec4(0.20f, 0.25f, 0.29f, 1.00f);
	colors[ImGuiCol_FrameBgHovered] = ImVec4(0.12f, 0.20f, 0.28f, 1.00f);
	colors[ImGuiCol_FrameBgActive] = ImVec4(0.09f, 0.12f, 0.14f, 1.00f);
	colors[ImGuiCol_TitleBg] = ImVec4(0.09f, 0.12f, 0.14f, 0.65f);
	colors[ImGuiCol_TitleBgActive] = ImVec4(0.08f, 0.10f, 0.12f, 1.00f);
	colors[ImGuiCol_TitleBgCollapsed] = ImVec4(0.00f, 0.00f, 0.00f, 0.51f);
	colors[ImGuiCol_MenuBarBg] = ImVec4(0.15f, 0.18f, 0.22f, 1.00f);
	colors[ImGuiCol_ScrollbarBg] = ImVec4(0.02f, 0.02f, 0.02f, 0.39f);
	colors[ImGuiCol_ScrollbarGrab] = ImVec4(0.20f, 0.25f, 0.29f, 1.00f);
	colors[ImGuiCol_ScrollbarGrabHovered] = ImVec4(0.18f, 0.22f, 0.25f, 1.00f);
	colors[ImGuiCol_ScrollbarGrabActive] = ImVec4(0.09f, 0.21f, 0.31f, 1.00f);
	colors[ImGuiCol_CheckMark] = ImVec4(0.28f, 0.56f, 1.00f, 1.00f);
	colors[ImGuiCol_SliderGrab] = ImVec4(0.28f, 0.56f, 1.00f, 1.00f);
	colors[ImGuiCol_SliderGrabActive] = ImVec4(0.37f, 0.61f, 1.00f, 1.00f);
	colors[ImGuiCol_Button] = ImVec4(0.20f, 0.25f, 0.29f, 1.00f);
	colors[ImGuiCol_ButtonHovered] = ImVec4(0.28f, 0.56f, 1.00f, 1.00f);
	colors[ImGuiCol_ButtonActive] = ImVec4(0.06f, 0.53f, 0.98f, 1.00f);
	colors[ImGuiCol_Header] = ImVec4(0.20f, 0.25f, 0.29f, 0.55f);
	colors[ImGuiCol_HeaderHovered] = ImVec4(0.26f, 0.59f, 0.98f, 0.80f);
	colors[ImGuiCol_HeaderActive] = ImVec4(0.26f, 0.59f, 0.98f, 1.00f);
	colors[ImGuiCol_Separator] = ImVec4(0.20f, 0.25f, 0.29f, 1.00f);
	colors[ImGuiCol_SeparatorHovered] = ImVec4(0.10f, 0.40f, 0.75f, 0.78f);
	colors[ImGuiCol_SeparatorActive] = ImVec4(0.10f, 0.40f, 0.75f, 1.00f);
	colors[ImGuiCol_ResizeGrip] = ImVec4(0.26f, 0.59f, 0.98f, 0.25f);
	colors[ImGuiCol_ResizeGripHovered] = ImVec4(0.26f, 0.59f, 0.98f, 0.67f);
	colors[ImGuiCol_ResizeGripActive] = ImVec4(0.26f, 0.59f, 0.98f, 0.95f);
	colors[ImGuiCol_Tab] = ImVec4(0.11f, 0.15f, 0.17f, 1.00f);
	colors[ImGuiCol_TabHovered] = ImVec4(0.26f, 0.59f, 0.98f, 0.80f);
	colors[ImGuiCol_TabActive] = ImVec4(0.20f, 0.25f, 0.29f, 1.00f);
	colors[ImGuiCol_TabUnfocused] = ImVec4(0.11f, 0.15f, 0.17f, 1.00f);
	colors[ImGuiCol_TabUnfocusedActive] = ImVec4(0.11f, 0.15f, 0.17f, 1.00f);
	colors[ImGuiCol_PlotLines] = ImVec4(0.61f, 0.61f, 0.61f, 1.00f);
	colors[ImGuiCol_PlotLinesHovered] = ImVec4(1.00f, 0.43f, 0.35f, 1.00f);
	colors[ImGuiCol_PlotHistogram] = ImVec4(0.90f, 0.70f, 0.00f, 1.00f);
	colors[ImGuiCol_PlotHistogramHovered] = ImVec4(1.00f, 0.60f, 0.00f, 1.00f);
	colors[ImGuiCol_TextSelectedBg] = ImVec4(0.26f, 0.59f, 0.98f, 0.35f);
	colors[ImGuiCol_DragDropTarget] = ImVec4(1.00f, 1.00f, 0.00f, 0.90f);
	colors[ImGuiCol_NavHighlight] = ImVec4(0.26f, 0.59f, 0.98f, 1.00f);
	colors[ImGuiCol_NavWindowingHighlight] = ImVec4(1.00f, 1.00f, 1.00f, 0.70f);
	colors[ImGuiCol_NavWindowingDimBg] = ImVec4(0.80f, 0.80f, 0.80f, 0.20f);
	colors[ImGuiCol_ModalWindowDimBg] = ImVec4(0.80f, 0.80f, 0.80f, 0.35f);
}

void Overlay::GameStart(MemSnapshot& memSnapshot)
{
	scriptManager.LoadAll(configs.GetStr("scriptsFolder", "."), memSnapshot.player->name);
}

void Overlay::StartFrame()
{
	MSG msg;
	ZeroMemory(&msg, sizeof(MSG));

	if (PeekMessage(&msg, NULL, 0U, 0U, PM_REMOVE))
	{
		TranslateMessage(&msg);
		DispatchMessage(&msg);
	}

	ImGui_ImplDX11_NewFrame();
	ImGui_ImplWin32_NewFrame();
	ImGui::NewFrame();
}

void Overlay::Update(MemSnapshot& memSnapshot) {

	// Simple check to see if game ended
	if (memSnapshot.champions.size() == 0 || !isWindowVisible)
		return;

	auto timeBefore = high_resolution_clock::now();
	PyGame state = PyGame::ConstructFromMemSnapshot(memSnapshot);

	DrawOverlayWindows(state);
	ExecScripts(state);
	DrawUI(state, memSnapshot);

	duration<float, std::milli> timeDuration = high_resolution_clock::now() - timeBefore;
	processTimeMs = timeDuration.count();
}

void Overlay::RenderFrame()
{
	static ImVec4 clear_color = ImVec4(0.f, 0.f, 0.f, 0.f);

	// Render
	auto timeBefore = high_resolution_clock::now();

	ImGui::EndFrame();
	ImGui::Render();
	dxDeviceContext->OMSetRenderTargets(1, &dxRenderTarget, NULL);
	dxDeviceContext->ClearRenderTargetView(dxRenderTarget, (float*)&clear_color);
	ImGui_ImplDX11_RenderDrawData(ImGui::GetDrawData());
	dxSwapChain->Present(0, 0);

	duration<float, std::milli> timeDuration = high_resolution_clock::now() - timeBefore;
	renderTimeMs = timeDuration.count();
}

void Overlay::ExecScripts(PyGame & state)
{
	for (auto& script : scriptManager.activeScripts) {
		if (script->enabled && script->loadError.empty() && script->execError.empty())
			script->ExecUpdate(state, imguiInterface);
	}
}

void Overlay::DrawUI(PyGame& state, MemSnapshot& memSnapshot) {

	high_resolution_clock::time_point timeBefore;

	ImGui::Begin("WS+ BCKD00R", nullptr, windowFlags | ImGuiWindowFlags_NoTitleBar | ImGuiWindowFlags_AlwaysAutoResize);

	if (ImGui::BeginTabBar("WinStealerTabBar", ImGuiTabBarFlags_Reorderable | ImGuiTabBarFlags_FittingPolicyScroll | ImGuiTabBarFlags_NoTooltip)) {
			DrawScriptSettings(state, memSnapshot);
		ImGui::EndTabBar();
	}

	ImGui::End();
}

void Overlay::DrawOverlayWindows(PyGame& state)
{
	// Draw game overlay (used for primitive rendering)
	auto io = ImGui::GetIO();
	ImGui::SetNextWindowSize(io.DisplaySize);
	ImGui::SetNextWindowPos(ImVec2(0, 0));
	ImGui::Begin("##Overlay", nullptr,
		windowFlags | ImGuiWindowFlags_NoTitleBar | ImGuiWindowFlags_AlwaysAutoResize
	);
	state.overlay = ImGui::GetWindowDrawList();
	ImGui::End();
}

void Overlay::DrawScriptSettings(PyGame& state, MemSnapshot& memSnapshot)
{
	int idNode = 10000;
	for (std::shared_ptr<Script>& script : scriptManager.activeScripts) {
		idNode++;

		// If we got any load/execution script error we should print it in bright red
		if (ImGui::BeginTabItem(script->name.c_str())) {
			if (!script->loadError.empty() || !script->execError.empty()) {
				DrawScriptError(script);
			}
			else {

				// Gray out disabled cheat
				bool skippedExecution = false;
				if (!script->enabled) {
					ImGui::PushStyleColor(ImGuiCol_Header, Colors::BLUE);
					skippedExecution = true;
				}
				ImGui::SetNextWindowSize({ 0.0f, 0.0f });
				ImGui::Begin(script->name.c_str(), nullptr, windowFlags);
				DrawScriptCommonSettings(script, idNode);
				script->ExecDrawSettings(state, imguiInterface);
				if (skippedExecution)
					ImGui::PopStyleColor();
				ImGui::End();
			}
		}

	}
}

void Overlay::DrawScriptError(std::shared_ptr<Script>& script)
{
	if (ImGui::BeginTabItem(script->name.c_str())) {
		ImGui::PushStyleColor(ImGuiCol_Header, Colors::ORANGE);
		if (ImGui::CollapsingHeader(script->name.c_str())) {
			if (ImGui::Button("Reload addon"))
				scriptManager.ReloadScript(script);

			ImGui::TextColored(Colors::ORANGE, script->loadError.c_str());
			ImGui::TextColored(Colors::ORANGE, script->execError.c_str());
		}
		ImGui::PopStyleColor();
	}
}

void Overlay::DrawScriptCommonSettings(std::shared_ptr<Script>& script, int id)
{
	if (ImGui::Button("Reload script"))
		scriptManager.ReloadScript(script);
	ImGui::SameLine();
	if (ImGui::Button("Save settings")) {
		scriptManager.SaveScriptConfigs(script);
		configs.SaveToFile();
	}
	ImGui::Checkbox("Enabled", &script->enabled);
	ImGui::Separator();
}

bool Overlay::IsVisible()
{
	return isWindowVisible;
}

void Overlay::Hide()
{
	ShowWindow(hWindow, SW_HIDE);
	isWindowVisible = false;
}

void Overlay::Show()
{
	ShowWindow(hWindow, SW_SHOW);
	isWindowVisible = true;
}

void Overlay::ToggleTransparent()
{
	LONG ex_style = GetWindowLong(hWindow, GWL_EXSTYLE);
	ex_style = (ex_style & WS_EX_TRANSPARENT) ? (ex_style & ~WS_EX_TRANSPARENT) : (ex_style | WS_EX_TRANSPARENT);
	SetWindowLong(hWindow, GWL_EXSTYLE, ex_style);
}

ID3D11Device * Overlay::GetDxDevice()
{
	return dxDevice;
}

bool Overlay::CreateDeviceD3D(HWND hWnd)
{
	const D3D_FEATURE_LEVEL featureLevelArray[2] = { D3D_FEATURE_LEVEL_11_0, D3D_FEATURE_LEVEL_10_0, };
	HCheck(D3D11CreateDevice(
		nullptr,    // Adapter
		D3D_DRIVER_TYPE_HARDWARE,
		nullptr,    // Module
		D3D11_CREATE_DEVICE_BGRA_SUPPORT ,
		nullptr, 0, // Highest available feature level
		D3D11_SDK_VERSION,
		&dxDevice,
		nullptr,    // Actual feature level
		&dxDeviceContext), "Creating device");

	IDXGIDevice* dxgiDevice;
	HCheck(dxDevice->QueryInterface(__uuidof(IDXGIDevice), (void **)& dxgiDevice), "Query DXGI Device");

	IDXGIAdapter * dxgiAdapter = 0;
	HCheck(dxgiDevice->GetParent(__uuidof(IDXGIAdapter), (void **)& dxgiAdapter), "Get DXGI Adapter");

	IDXGIFactory2 * dxgiFactory = 0;
	HCheck(dxgiAdapter->GetParent(__uuidof(IDXGIFactory2), (void **)& dxgiFactory), "Get DXGI Factory");

	// Create swap chain with alpha mode premultiplied
	DXGI_SWAP_CHAIN_DESC1 description = {};
	description.Format = DXGI_FORMAT_B8G8R8A8_UNORM;
	description.BufferUsage = DXGI_USAGE_RENDER_TARGET_OUTPUT;
	description.SwapEffect = DXGI_SWAP_EFFECT_FLIP_SEQUENTIAL;
	description.BufferCount = 2;
	description.SampleDesc.Count = 1;
	description.AlphaMode = DXGI_ALPHA_MODE_PREMULTIPLIED;
	description.Scaling = DXGI_SCALING_STRETCH;
	RECT rect = {};
	GetClientRect(hWnd, &rect);
	description.Width = rect.right - rect.left;
	description.Height = rect.bottom - rect.top;

	HCheck(dxgiFactory->CreateSwapChainForComposition(dxgiDevice,
		&description,
		nullptr,
		&dxSwapChain), "Create swap chain");
		
	// Create Direct Composition layer
	IDCompositionDevice* dcompDevice;
	DCompositionCreateDevice(
		dxgiDevice,
		__uuidof(dcompDevice),
		(void**)&dcompDevice);

	IDCompositionTarget* target;
	dcompDevice->CreateTargetForHwnd(hWnd,
		true,
		&target);

	IDCompositionVisual* visual;
	dcompDevice->CreateVisual(&visual);
	visual->SetContent(dxSwapChain);
	target->SetRoot(visual);
	dcompDevice->Commit();

	CreateRenderTarget();
	return true;
}

void Overlay::CleanupDeviceD3D()
{
	CleanupRenderTarget();
	if (dxSwapChain) { dxSwapChain->Release(); dxSwapChain = NULL; }
	if (dxDeviceContext) { dxDeviceContext->Release(); dxDeviceContext = NULL; }
	if (dxDevice) { dxDevice->Release(); dxDevice = NULL; }
}

void Overlay::CreateRenderTarget()
{
	ID3D11Resource* pBackBuffer;
	if(S_OK != dxSwapChain->GetBuffer(0, IID_PPV_ARGS(&pBackBuffer)))
		throw std::runtime_error("Failed to retrieve DX11 swap chain buffer");
	if (S_OK != dxDevice->CreateRenderTargetView(pBackBuffer, NULL, &dxRenderTarget))
		throw std::runtime_error("Failed to create DX11 render target");
	pBackBuffer->Release();
}

void Overlay::CleanupRenderTarget()
{
	if (dxRenderTarget) { dxRenderTarget->Release(); dxRenderTarget = NULL; }
}

extern IMGUI_IMPL_API LRESULT ImGui_ImplWin32_WndProcHandler(HWND hWnd, UINT msg, WPARAM wParam, LPARAM lParam);
LRESULT WINAPI Overlay::WndProc(HWND hWnd, UINT msg, WPARAM wParam, LPARAM lParam)
{
	if (ImGui_ImplWin32_WndProcHandler(hWnd, msg, wParam, lParam))
		return true;

	switch (msg)
	{
	case WM_SIZE:
		if (dxDevice != NULL && wParam != SIZE_MINIMIZED)
		{
			CleanupRenderTarget();
			dxSwapChain->ResizeBuffers(0, (UINT)LOWORD(lParam), (UINT)HIWORD(lParam), DXGI_FORMAT_UNKNOWN, 0);
			CreateRenderTarget();
		}
		return 0;
	case WM_SYSCOMMAND:
		if ((wParam & 0xfff0) == SC_KEYMENU) // Disable ALT application menu
			return 0;
		break;
	case WM_DESTROY:
		::PostQuitMessage(0);
		return 0;
	}
	return ::DefWindowProc(hWnd, msg, wParam, lParam);
}