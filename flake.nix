{
  description = "研究计划草稿技能及固定运行环境（苹果芯片 Mac、Codex）";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/6510408d147d8c5e6d76043e899e9251756f6a75";

    agent-env-nix = {
      url = "github:RekiDunois/agent-env-nix/c368871942435bdc178a1063ce9c677acaf8cabc";
      inputs.nixpkgs.follows = "nixpkgs";
    };

    professor-contact = {
      url = "github:ScholarWorkflow/professor-contact/ad096fe31a4b5694cbe47a40f37b621435e1eeec";
      inputs.nixpkgs.follows = "nixpkgs";
      inputs.agent-env-nix.follows = "agent-env-nix";
    };
  };

  outputs = { self, nixpkgs, agent-env-nix, professor-contact }:
    let
      system = "aarch64-darwin";
      pkgs = nixpkgs.legacyPackages.${system};
      shared = agent-env-nix.lib;

      # 递归依赖取自 professor-contact 已锁定的实例，避免同一上游包在本仓库
      # 求值出第二份构建上下文；顶层 nixpkgs 与 agent-env-nix 由本 flake 声明，
      # 使用方可以 follows 到自己的输入。
      research = professor-contact.inputs.professor-research;
      base = professor-contact.inputs.base-skills;
      source = research.inputs.browser-pdf-tools.inputs.source-access-skills;

      products = import ./nix/research-proposal.nix {
        inherit pkgs;
        inherit (shared) mkAgentPackage mkProject;
        contactRuntime = professor-contact.packages.${system}.professor-contact-runtime;
        visionGlance = base.apps.${system}.vision-glance.program;
        agentDependencies = [
          professor-contact.packages.${system}.professor-contact
          research.packages.${system}.professor-collector
          research.packages.${system}.professor-topic-clustering
          source.packages.${system}.duckduckgo-search
          source.packages.${system}.yahoo-japan-search
          base.packages.${system}.vision-tools
        ];
      };
    in
    {
      packages.${system} = {
        research-proposal-runtime = products.runtime;
        research-proposal = products.package;
        research-proposal-environment = products.project;
        research-proposal-activate = shared.mkCachedActivation {
          inherit pkgs;
          environment = products.project;
          name = "research-proposal-activate";
        };
        default = products.package;
      };
    };
}
