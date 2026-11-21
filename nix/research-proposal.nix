{ pkgs
, mkAgentPackage
, mkProject
, contactRuntime
, visionGlance
, agentDependencies
}:

let
  inherit (pkgs) lib;
  version = "0.1.0";

  # 只生成安装位置；业务代码始终取自技能目录中的同一份源码。
  fixedTools = {
    pandoc = "${pkgs.pandoc}/bin/pandoc";
    soffice = "${pkgs.libreoffice-bin}/Applications/LibreOffice.app/Contents/MacOS/soffice";
    vision-glance = visionGlance;
    contact_targets = "${contactRuntime}/scripts/contact_targets";
    contact_stage1 = "${contactRuntime}/scripts/contact_stage1";
    contact_state = "${contactRuntime}/scripts/contact_state";
  };
  toolLocations = pkgs.writeText "research-proposal-runtime-tools.py" ''
    # 由固定 Nix 输入生成，仅记录运行程序位置。
    TOOLS = ${builtins.toJSON fixedTools}
  '';

  module = pkgs.python3Packages.buildPythonPackage {
    pname = "research-proposal";
    inherit version;
    format = "other";
    src = lib.cleanSourceWith {
      src = ../skills/research-proposal/scripts/research_proposal;
      filter = path: type:
        builtins.baseNameOf path != "__pycache__"
        && !(lib.hasSuffix ".pyc" path);
    };
    dontConfigure = true;
    dontBuild = true;
    doCheck = false;
    propagatedBuildInputs = with pkgs.python3Packages; [
      pymupdf
      pillow
      python-docx
      lxml
    ];
    installPhase = ''
      runHook preInstall
      mkdir -p "$out/${pkgs.python3.sitePackages}/research_proposal"
      cp -R ./. "$out/${pkgs.python3.sitePackages}/research_proposal/"
      chmod -R u+w "$out/${pkgs.python3.sitePackages}/research_proposal"
      cp ${toolLocations} "$out/${pkgs.python3.sitePackages}/research_proposal/_runtime.py"
      runHook postInstall
    '';
  };

  # 把模块装进解释器环境，使用 uv --python 时也能保持同一套模块与库。
  python = pkgs.python3.withPackages (ps: [
    module
    ps.pymupdf
    ps.pillow
    ps.python-docx
    ps.lxml
  ]);

  runtime = pkgs.runCommand "research-proposal-runtime" { } ''
    mkdir -p "$out/bin"
    ln -s ${python}/bin/python3 "$out/bin/python3"
    ln -s ${pkgs.pandoc}/bin/pandoc "$out/bin/pandoc"
    cat > "$out/bin/proposal-runtime" <<'EOF'
    #!${pkgs.bash}/bin/bash
    set -euo pipefail
    exec ${python}/bin/python3 -I -B -m research_proposal "$@"
    EOF
    chmod 0555 "$out/bin/proposal-runtime"
  '';

  # 复制完整资源，只把公开启动脚本接到固定运行包。
  skill = pkgs.runCommand "research-proposal-skill" { } ''
    mkdir -p "$out"
    cp -R ${../skills/research-proposal}/. "$out/"
    chmod -R u+w "$out"
    cat > "$out/scripts/proposal-runtime" <<'EOF'
    #!${pkgs.bash}/bin/bash
    exec ${runtime}/bin/proposal-runtime "$@"
    EOF
    chmod 0555 "$out/scripts/proposal-runtime"
    cat > "$out/scripts/pandoc" <<'EOF'
    #!${pkgs.bash}/bin/bash
    exec ${pkgs.pandoc}/bin/pandoc "$@"
    EOF
    chmod 0555 "$out/scripts/pandoc"
  '';

  package = mkAgentPackage {
    inherit pkgs version agentDependencies;
    id = "research-proposal";
    files."skills/research-proposal" = skill;
    exports.skills.research-proposal = "skills/research-proposal";
    runtimePackages = [ runtime ];
    enableHarnesses = [ "codex" ];
  };

  project = mkProject {
    inherit pkgs;
    name = "research-proposal-environment";
    roots = [ package ];
  };
in
{
  inherit runtime package project;
}
