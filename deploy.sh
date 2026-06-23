#!/bin/bash
set -e
cd "$(dirname "$0")"

REPO="gourry7/asungvoice"
SSH_KEY="$HOME/.ssh/id_ed25519_github"

echo "▶ 아성보이스 사이트 GitHub 배포"
echo "  대상: https://github.com/$REPO"

if ! ssh -T -i "$SSH_KEY" git@github.com 2>&1 | grep -q "gourry7"; then
  echo "❌ GitHub SSH 인증 실패. ~/.ssh/id_ed25519_github 키를 확인하세요."
  exit 1
fi

if curl -sf "https://api.github.com/repos/$REPO" >/dev/null 2>&1; then
  echo "✓ 저장소 존재 확인"
else
  echo "📦 저장소 생성 중..."
  if command -v gh >/dev/null && gh auth status >/dev/null 2>&1; then
    gh repo create asungvoice --public --description "아성보이스 워치독 비명감지기 홈페이지"
  else
    echo ""
    echo "먼저 GitHub에서 저장소를 생성해 주세요:"
    echo "  https://github.com/new → Repository name: asungvoice → Public → Create"
    echo ""
    read -p "저장소 생성 완료 후 Enter..."
  fi
fi

git remote remove origin 2>/dev/null || true
git remote add origin "git@github.com:$REPO.git"

export GIT_SSH_COMMAND="ssh -i $SSH_KEY -o StrictHostKeyChecking=no"
git branch -M main
git push -u origin main --force

echo ""
echo "✅ 배포 완료!"
echo "   GitHub Pages 활성화: Settings → Pages → Branch: main / root"
echo "   URL: https://gourry7.github.io/asungvoice/"
