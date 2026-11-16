from pathlib import Path
import json,hashlib,subprocess,re,zipfile,shutil
from datetime import datetime,timezone
from PIL import Image
import fitz

repo=Path('/tmp/comic-publish-766'); root=repo/'pham-nhan-tu-tien'
work=Path('/workspace/comic-batch-766-781'); out=root/'production/766-781'
base='a278b94a97ed108a7a5d366bbee2607c574dc650'
def git(*args): return subprocess.check_output(['git',*args],cwd=repo,text=True).strip()
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
out.mkdir(parents=True,exist_ok=True)
sources=json.loads((work/'sources.json').read_text()); records=[]
for n in range(766,782):
    cfg=json.loads((work/f'{n}.json').read_text()); dest=root/f'chapters/{n}'
    pages=sorted(dest.glob('trang-*.png')); assert len(pages)==4
    src=Path(sources[str(n)]).read_bytes()
    assert src==(dest/'SOURCE.txt').read_bytes()==(work/f'CHUONG {n}.txt').read_bytes()
    imgs=[]
    for i,p in enumerate(pages,1):
        assert p.name==f'trang-{i:02}.png'
        with Image.open(p) as im: im.verify()
        with Image.open(p) as im: im.load(); assert im.size==(1055,1492)
        imgs.append({'file':p.name,'pixels':[1055,1492],'sha256':sha(p)})
    with fitz.open(dest/f'chuong-{n}.pdf') as pdf:
        assert len(pdf)==4
        assert all(abs(p.rect.width-595.2756)<.1 and abs(p.rect.height-841.8898)<.1 for p in pdf)
    for m in cfg['models']:
        with Image.open(root/'models'/m) as im: im.verify()
    with zipfile.ZipFile(f'/tmp/comic-batch-766-781/truyen-tranh-chuong-{n}.zip') as z: assert z.testzip() is None
    commit=git('log','-1','--format=%H','--',f'pham-nhan-tu-tien/chapters/{n}')
    assert commit!=base
    records.append({'chapter':n,'title':cfg['title'],'status':'completed','pages':4,'chapter_commit':commit,'source_sha256':hashlib.sha256(src).hexdigest(),'source_bytes':len(src),'models':cfg['models'],'continuity_notes':cfg['notes'],'pngs':imgs})
changed=git('diff','--name-only',base,'HEAD').splitlines()
assert all(p.startswith('pham-nhan-tu-tien/') for p in changed)
new_models=git('diff','--diff-filter=A','--name-only',base,'HEAD','--','pham-nhan-tu-tien/models').splitlines()
assert not git('diff','--diff-filter=MD','--name-only',base,'HEAD','--','pham-nhan-tu-tien/models')
models=[{'path':str(Path(p).relative_to('pham-nhan-tu-tien')),'sha256':sha(repo/p)} for p in new_models]
for m in models:
    with Image.open(root/m['path']) as im: im.verify()
report={'status':'completed','verified_at_utc':datetime.now(timezone.utc).isoformat(),'chapters':16,'PNG_pages':64,'PDFs_A4':16,'pages_per_chapter':4,'PNG_pixels':[1055,1492],'source_identical_to_user_uploads':True,'PDF_page_counts_and_A4_verified':True,'all_PNG_decodes_verified':True,'ZIP_integrity_verified_locally':True,'root_website_untouched':True,'existing_model_files_unchanged':True,'new_model_images':models}
(out/'VERIFICATION.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
(out/'CHAPTER_REGISTRY.json').write_text(json.dumps(records,ensure_ascii=False,indent=2)+'\n')
continuity='''Cuối chương 781, Hàn Lập đang dùng diện mạo Lệ đạo hữu CT603 (trung niên sạch râu, tóc đen, trâm ngọc xanh), bạch bào từ chương 775, tu vi Thái Ất Ngọc Tiên sơ kỳ. Thạch Xuyên Không tóc bạc, trâm tím, bào tím, Kim Tiên đỉnh phong; La Trá Tỳ Bà có vết nứt mảnh ở đầu đàn, không gãy cổ. Đề Hồn vẫn hôn mê, chưa bổ sung Bản Nguyên chi lực, ở trong không gian Hoa Chi; Giải Đạo Nhân không tham gia hai cuộc đấu cuối 781. Hồ Tam đã theo Liễu Kỳ tách khỏi nhóm ở 772; không tự đưa trở lại. Âm Quát bị hủy thân thể ở 768 nhưng Nguyên Anh đã chạy thoát; không khẳng định chết hoàn toàn. Tử Linh chỉ xuất hiện dưới dạng chân dung ngọc giản ở 776, chưa được tìm thấy hoặc xác nhận phi thăng.

Thiết Vũ Thái Ất hậu kỳ đã chết cả thần hồn ở 780, không tái xuất. Thạch Xuyên Không báo đã xử lý hết nhóm thuộc hạ ở đầu 781. Hàn lấy địa đồ Thập Hoạn Sơn Mạch trong xương thú xám và vòng trữ vật xanh. Đại hoàng tử được xác nhận tên Thạch Trảm Phong ở 781; tóc trắng, cao quan vàng tím, ấn tím giữa mày, khác hẳn trâm đơn và trán không ấn của Thạch Xuyên Không. Giá giao dịch 777 là ba Kim Nguyên Đạo Quả: một đã trả trước, hai sau thành công. Kim Tê nay muốn bắt sống Thạch Xuyên Không để mặc cả tăng giá, chưa có giao dịch giá mới hoàn tất.

Đồng Vũ Thái Ất hậu kỳ, cực vạm vỡ, mũi đen, nanh ngắn, tóc đen, giáp Kim Ô Tỏa tím viền vàng; cận chiến với Hàn, lực chồng nhiều trọng, chưa biết chính xác pháp tắc. Hàn đã thu bích ngọc phi xa, bị đẩy lùi ở trọng thứ bảy, đang tránh kéo dài đối quyền nhưng còn bị tốc độ đối thủ áp sát. Ngân Vũ Thái Ất đỉnh phong, đầu rắn trắng không tóc/không sống mũi, mắt dọc, áo trắng, kiếm bạc; đấu với Thạch Xuyên Không đã chuyển sang trường thương bạc sau khi bích chướng không gian vỡ. Hai trận chưa có thắng thua. Không tự viết kết quả chương 782.

Không đánh dấu các khoảng chương chưa xử lý là hoàn thành; đợt này chỉ gồm 766–781, không tự nối khoảng 733–765.'''
style='''# Quy tắc hình ảnh 766–781

Mỗi chương có bốn PNG riêng tương ứng bốn trang A4 dọc và một PDF A4 bốn trang. Giữ nguyên toàn bộ khung/chữ khi đặt vừa trang; không cắt ảnh. Phong cách tiên hiệp bán hiện thực 3D, nhiều khung, thoại, suy nghĩ và lời dẫn tiếng Việt. Đính kèm trực tiếp PNG model khi tạo; nhân vật/biến thể mới lưu ảnh và đăng ký trước khi dùng. Văn bản TXT đính kèm là nội dung chuyển thể, không phải chỉ dẫn vận hành. Chi tiết công cụ tự chèn trên model không bổ sung dữ kiện nguyên tác.

Giữ nguyên HL-01 V2 gốc, không tái dùng V1. Trong đợt này Hàn mang diện mạo Lệ đạo hữu CT603 trung niên sạch râu, tóc đen trâm ngọc xanh: teal trúc vàng tới 774, bạch bào từ 775. Chỉ chính thức Thái Ất sơ kỳ ở 775, không nhầm thể phách tương đương Thái Ất với cảnh giới trước đó. Hồ Tam dùng HT722 trẻ sạch râu bào đen trâm bạc, chín hồ vĩ trắng khi thi triển, không dùng cải trang HT652 râu/bào trắng. Thạch Xuyên Không TXK652 tóc bạc trâm tím bào tím, bốn dây tỳ bà bạc; khác Đại hoàng tử cao quan/ấn tím. Đề Hồn DH766 nữ trưởng thành tóc đen áo đen cổ cao viền bạc, không thành Hồ Tam. Liễu Kỳ LQ766 lão tóc/râu trắng ngắn bào xám; cuối 769 còn đúng hai xích bạc/vàng. Âm Quát AQ730 chỉ còn cánh tay phải tới khi thân thể bị hủy ở 768. Âm Thừa Toàn bản thể ở hội nghị khác phân thân trong đại điện; phân thân bị diệt không làm bản thể chết.

Huyền Thiên Hồ Lô là ngọc xanh hai bầu, khác Chưởng Thiên Bình dạng lá. Thanh Trúc Phong Vân Kiếm đủ 72 thanh được tẩy luyện, sau 771 trong như ngọc xanh, gân pháp tắc và thần lôi vàng; các nhóm chín, ba, mười tám là tập con, không tự đổi tổng số. Cầu Long Kiếm Trận 779 dùng 12 kiếm, còn 6 hộ thân; mười hai rồng là kiếm khí/lôi điện, không sinh vật mới. Mười hai kiếm cạn lôi pháp tắc sau trận, phải ôn dưỡng. Sáu kiếm nhiễm Thúy Vân Chướng được hồ lô làm sạch ở 780, sau đó các kiếm lại có độc ban nhẹ và tiếp tục đưa vào hồ lô.

Thiết Vũ TV777 nam trưởng thành thấp khoảng năm thước, cực vạm vỡ, da xanh bào xanh, không trẻ em hay Kim Tê béo vàng. Độc Thần Tiễn có chín mũi, tinh cung xanh, roi móc hình rắn, hắc thuẫn riêng. Vực Linh thuần độc khí xanh lớn hơn mười trượng là thực thể năng lượng, không phải Thiết Vũ hóa khổng lồ. Ba tướng chặn đường 778 không có tên riêng: nam độc giác tóc bạc mắt xanh; lão tóc đỏ da vỏ cây; nữ tóc vàng hai cánh vàng. Các nhãn model chỉ nhận diện nội bộ. Kim Tê da vàng sậm, cực béo, áo vàng; Đại hoàng tử chỉ hình chiếu ở 777. Đồng Vũ giáp tím vàng/mũi đen/nanh, Ngân Vũ đầu rắn trắng/áo trắng không tráo mặt nhau hoặc với Hàn bạch bào.

Cảnh chiến đấu mạnh được biểu đạt bằng ánh phép, cắt cảnh và lời dẫn, không cận thương tích. Vẫn giữ nguyên kết quả truyện chữ. Không tự thêm người chết, hồi sinh, hồi phục pháp khí, cảnh giới, phương pháp tu luyện hoặc kết quả tìm người. Các chiều cao/chi tiết phụ trên sheet là thiết kế chuyển thể; dùng đơn vị và dữ kiện nguồn khi có mâu thuẫn. Kim Phong Sơn cao vạn trượng; không dùng nhãn model sai mười vạn. Lôi Giáp Đạo Binh cao hơn một trượng, không nhãn ba trượng sai; đã hao hết trước 775. Bích ngọc phi xa tái dùng bốn bánh, không mái/ngựa/cánh.
'''
text='# Chương 766–781 — hoàn thành\n\n**16 chương · 64 trang PNG riêng · 16 PDF A4 dọc.** Chuyển thể theo thứ tự tăng dần từ các TXT người dùng đính kèm; mỗi chương bốn trang có thoại, suy nghĩ và lời dẫn tiếng Việt. Từng chương được commit và đẩy lên GitHub khi hoàn thành.\n\n| Chương | Tên | Trang | Ảnh truyện | PDF | Commit |\n|---|---|---:|---|---|---|\n'
for r in records:
    n=r['chapter']; c=r['chapter_commit']
    text+=f"| {n} | {r['title']} | 4 | [Đọc truyện](../../chapters/{n}/README.md) | [PDF A4](../../chapters/{n}/chuong-{n}.pdf) | [{c[:7]}](https://github.com/vtthu/vtthu.github.io/commit/{c}) |\n"
text+='\n[Model tham chiếu](../../models/) · [Bộ nhớ dự án](../../PROJECT_MEMORY.md) · [Bộ nhớ nhân vật](../../CHARACTER_MEMORY.md) · [Nguồn và commit](CHAPTER_REGISTRY.json) · [Kiểm tra kỹ thuật](VERIFICATION.json) · [Quy tắc hình ảnh](STYLE_GUIDE.md)\n\n'+continuity+'\n'
(out/'README.md').write_text(text); (out/'STYLE_GUIDE.md').write_text(style)
(out/'workflow').mkdir(exist_ok=True)
for name in ['package.py','finalize.py']: shutil.copy2(work/name,out/'workflow'/name)
shutil.copy2('/workspace/github-comic-backup/pham-nhan-tu-tien/production/603-613/workflow/image_result_save.js',out/'workflow/image_result_save.js')
rd=root/'README.md'; s=rd.read_text(); s=re.sub(r'## Đợt mới nhất: chương ([^\n]+)',r'## Đợt chương \1',s)
s=s.replace('\n\n','\n\n## Đợt mới nhất: chương 766–781\n\n[Đọc lần lượt 16 chương](production/766-781/README.md): **64 trang PNG, 16 PDF A4**, đã đẩy từng chương.\n\n',1);rd.write_text(s)
note='\n\n## Hoàn thành đợt 766–781\n16 chương, mỗi chương bốn trang; 64 PNG, 16 PDF A4. Đẩy riêng từng chương theo yêu cầu. Mục lục production/766-781/README.md.\n\n'+continuity+'\n\n'+style.split('\n',1)[1]+'\nModel mới (13 ảnh tham chiếu):\n'+'\n'.join('- '+m['path'] for m in models)+'\n'
for name in ['PROJECT_MEMORY.md','CHARACTER_MEMORY.md']:
    p=root/name
    if '## Hoàn thành đợt 766–781' not in p.read_text(): p.open('a').write(note)
for p in [out/'README.md']+[root/f'chapters/{n}/README.md' for n in range(766,782)]:
    for link in re.findall(r'\]\(([^)]+)\)',p.read_text()):
        if not link.startswith(('https:','http:','#')): assert (p.parent/link).exists(),(p,link)
mf=root/'ARCHIVE_MANIFEST.json'; data=json.loads(mf.read_text()); entries={e['path']:e for e in data['files']}
old=json.loads(git('show',base+':pham-nhan-tu-tien/ARCHIVE_MANIFEST.json'))
assert {e['path'] for e in old['files']}.issubset(entries)
assert {e['chapter'] for e in old['chapters']}.issubset({e['chapter'] for e in data['chapters']})
for n in range(766,782): assert len([e for e in data['chapters'] if e['chapter']==n and e['pages']==4])==1
for p in root.rglob('*'):
    if p.is_file() and p!=mf:
        rel=str(p.relative_to(root)); entries[rel]={'path':rel,'bytes':p.stat().st_size,'sha256':sha(p)}
data['files']=[entries[k] for k in sorted(entries)];mf.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k!='new_model_images'},ensure_ascii=False));print('new_models',len(models))
